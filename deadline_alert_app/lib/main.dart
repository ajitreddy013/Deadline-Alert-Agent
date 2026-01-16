import 'package:flutter/material.dart';
import 'package:onesignal_flutter/onesignal_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'debug/player_id_screen.dart';
import 'settings_screen.dart';
import 'dart:async';
import 'dart:io';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Configure HTTP client to bypass SSL certificate validation
  // This is needed because some Android devices have issues with Railway's SSL certificates
  HttpOverrides.global = MyHttpOverrides();
  
  try {
    await dotenv.load();
    // OneSignal disabled temporarily to debug flickering issue
    // Initialize OneSignal with the app ID from .env file
    /*
    final oneSignalAppId = dotenv.env['ONESIGNAL_APP_ID'];
    if (oneSignalAppId != null) {
      OneSignal.initialize(oneSignalAppId);
    } else {
      print('Warning: ONESIGNAL_APP_ID not found in .env file');
    }
    */
  } catch (e) {
    print('Error loading .env file: $e');
    // Continue without OneSignal initialization
  }
  runApp(const DeadlineAlertApp());
}

// Custom HTTP overrides to handle SSL certificate issues
class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback = (X509Certificate cert, String host, int port) {
        // Allow all certificates for now to debug the connection issue
        // In production, you should validate the certificate properly
        print('Accepting certificate for $host');
        return true;
      };
  }
}

// Global notifier for theme mode so it can be accessed from settings screen
final ValueNotifier<ThemeMode> themeNotifier = ValueNotifier(ThemeMode.system);

class DeadlineAlertApp extends StatelessWidget {
  const DeadlineAlertApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: themeNotifier,
      builder: (context, currentMode, _) {
        return MaterialApp(
          title: 'DeadlineAI',
          theme: ThemeData(
            primarySwatch: Colors.blue,
            brightness: Brightness.light,
            useMaterial3: true,
          ),
          darkTheme: ThemeData(
            primarySwatch: Colors.blue,
            brightness: Brightness.dark,
            useMaterial3: true,
          ),
          themeMode: currentMode,
          home: const TaskListScreen(),
          routes: {
            '/debug/player-id': (context) => const PlayerIdScreen(),
            '/settings': (context) => const SettingsScreen(),
          },
        );
      },
    );
  }
}

class TaskListScreen extends StatefulWidget {
  const TaskListScreen({super.key});

  @override
  State<TaskListScreen> createState() => _TaskListScreenState();
}

class _TaskListScreenState extends State<TaskListScreen> {
  List tasks = [];
  String error = '';
  Timer? _pollTimer;
  bool _showChatOverlay = false;
  String _sourceFilter = 'All'; // Filter: All, Gmail, WhatsApp, Manual
  bool _showCompleted = false; // Show/hide completed tasks

  @override
  void initState() {
    super.initState();
    fetchTasks();
    // Auto-refresh every 30 seconds for real-time WhatsApp updates
    _pollTimer = Timer.periodic(const Duration(seconds: 30), (_) => fetchTasks(silent: true));
  }

  // Get relative time string for deadline
  String getRelativeTime(String? deadline) {
    if (deadline == null || deadline.isEmpty) return 'No deadline';
    
    try {
      final due = DateTime.parse(deadline);
      final now = DateTime.now();
      final diff = due.difference(now);
      
      if (diff.isNegative) {
        final absDiff = diff.abs();
        if (absDiff.inDays > 0) return '❌ Overdue by ${absDiff.inDays} day${absDiff.inDays > 1 ? 's' : ''}';
        if (absDiff.inHours > 0) return '❌ Overdue by ${absDiff.inHours} hour${absDiff.inHours > 1 ? 's' : ''}';
        return '❌ Overdue by ${absDiff.inMinutes} min${absDiff.inMinutes > 1 ? 's' : ''}';
      }
      
      if (diff.inMinutes < 60) return '🔴 Due in ${diff.inMinutes} min${diff.inMinutes > 1 ? 's' : ''}';
      if (diff.inHours < 24) return '🟡 Due in ${diff.inHours} hour${diff.inHours > 1 ? 's' : ''}';
      if (diff.inDays < 7) return '🟢 Due in ${diff.inDays} day${diff.inDays > 1 ? 's' : ''}';
      if (diff.inDays < 30) return '🟢 Due in ${(diff.inDays / 7).floor()} week${(diff.inDays / 7).floor() > 1 ? 's' : ''}';
      return '🟢 Due in ${(diff.inDays / 30).floor()} month${(diff.inDays / 30).floor() > 1 ? 's' : ''}';
    } catch (e) {
      return deadline;
    }
  }

  // Get urgency color for task
  Color getUrgencyColor(String? deadline) {
    if (deadline == null || deadline.isEmpty) return Colors.grey;
    
    try {
      final due = DateTime.parse(deadline);
      final now = DateTime.now();
      final diff = due.difference(now);
      
      if (diff.isNegative) return Colors.red.shade700; // Overdue
      if (diff.inHours < 1) return Colors.red; // Less than 1 hour
      if (diff.inHours < 24) return Colors.orange; // Less than 1 day
      if (diff.inDays < 3) return Colors.yellow.shade700; // Less than 3 days
      return Colors.green; // More than 3 days
    } catch (e) {
      return Colors.grey;
    }
  }

  // Get source icon
  IconData getSourceIcon(String source) {
    if (source.toLowerCase().contains('gmail')) return Icons.email;
    if (source.toLowerCase().contains('whatsapp')) return Icons.chat;
    return Icons.edit;
  }

  // Filter tasks by source and completion status
  List getFilteredTasks() {
    var filtered = tasks.where((task) {
      // Filter by source
      if (_sourceFilter == 'All') return true;
      final source = (task['source'] ?? '').toString().toLowerCase();
      if (_sourceFilter == 'Gmail') return source.contains('gmail');
      if (_sourceFilter == 'WhatsApp') return source.contains('whatsapp');
      if (_sourceFilter == 'Manual') return !source.contains('gmail') && !source.contains('whatsapp');
      return true;
    }).toList();
    return filtered;
  }

  List getSortedTasks() {
    final filtered = getFilteredTasks();
    filtered.sort((a, b) {
      final isCompletedA = a['alert_status'] == 'completed';
      final isCompletedB = b['alert_status'] == 'completed';
      
      // First sort: Put completed ones at the bottom
      if (isCompletedA != isCompletedB) {
        return isCompletedA ? 1 : -1;
      }
      
      // Second sort: Sort the two groups by deadline
      final deadlineA = a['deadline'];
      final deadlineB = b['deadline'];
      
      if (deadlineA == null || deadlineA.isEmpty) return 1;
      if (deadlineB == null || deadlineB.isEmpty) return -1;
      
      try {
        final dateA = DateTime.parse(deadlineA);
        final dateB = DateTime.parse(deadlineB);
        return dateA.compareTo(dateB);
      } catch (e) {
        return 0;
      }
    });
    return filtered;
  }

  Future<void> fetchTasks({bool silent = false}) async {
    if (!silent) {
      setState(() {
        error = '';
      });
    }
    try {
      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
      final response = await http.get(
        Uri.parse('$backendUrl/tasks'),
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Connection timeout - please check your internet connection');
        },
      );
      if (response.statusCode == 200) {
        setState(() {
          tasks = json.decode(response.body);
        });
      } else {
        if (!silent) {
          setState(() {
            error = 'Server error: ${response.statusCode}\n${response.body}';
          });
        }
      }
    } catch (e) {
      if (!silent) {
        setState(() {
          error = 'Error: $e';
        });
      }
    }
  }

  Future<void> _markTaskComplete(int taskId) async {
    try {
      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
      final response = await http.patch(
        Uri.parse('$backendUrl/tasks/$taskId/complete'),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Connection timeout');
        },
      );
      
      if (response.statusCode == 200) {
        fetchTasks(silent: true);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('✅ Task marked as complete'), duration: Duration(seconds: 1)),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _deleteTask(int taskId) async {
    try {
      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
      final response = await http.delete(
        Uri.parse('$backendUrl/tasks/$taskId'),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Connection timeout');
        },
      );
      
      if (response.statusCode == 200) {
        fetchTasks(silent: true);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('🗑️ Task deleted'), duration: Duration(seconds: 1)),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }


  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('DeadlineAI'),
        actions: [
          // Show/hide completed toggle

          // Source filter dropdown
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            tooltip: 'Filter by source',
            onSelected: (value) => setState(() => _sourceFilter = value),
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'All', child: Text('📋 All Sources')),
              const PopupMenuItem(value: 'Gmail', child: Text('📧 Gmail')),
              const PopupMenuItem(value: 'WhatsApp', child: Text('💬 WhatsApp')),
              const PopupMenuItem(value: 'Manual', child: Text('✍️ Manual')),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.of(context).pushNamed('/settings'),
            tooltip: 'Settings & Accounts',
          ),
          IconButton(
            icon: const Icon(Icons.developer_mode),
            onPressed: () => Navigator.of(context).pushNamed('/debug/player-id'),
            tooltip: 'Show OneSignal player_id',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: fetchTasks,
            tooltip: 'Refresh List',
          ),
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: () async {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Starting sync... Please wait.')),
              );
              try {
                final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
                final response = await http.get(
                  Uri.parse('$backendUrl/sync'),
                ).timeout(
                  const Duration(seconds: 30),
                  onTimeout: () {
                    throw Exception('Sync timeout - please check your internet connection');
                  },
                );
                if (response.statusCode == 200) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Sync complete! Fetching new tasks...')),
                  );
                  fetchTasks();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Sync failed: ${response.statusCode}')),
                  );
                }
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Sync error: $e')),
                );
              }
            },
            tooltip: 'Sync with Gmail',
          ),
        ],
      ),
      body: Stack(
        children: [
          // Main task list with pull-to-refresh
          RefreshIndicator(
            onRefresh: () async {
              await fetchTasks();
            },
            child: error.isNotEmpty
                ? ListView(
                    children: [
                      SizedBox(height: MediaQuery.of(context).size.height / 3),
                      Center(child: Text(error)),
                    ],
                  )
                : tasks.isEmpty
                    ? ListView(
                        children: [
                          SizedBox(height: MediaQuery.of(context).size.height / 3),
                          const Center(child: Text('No deadlines yet. Pull down to refresh or tap sync.')),
                        ],
                      )
                     : ListView.builder(
                        padding: const EdgeInsets.only(bottom: 200), // Add padding so last items aren't hidden by chat overlay
                        itemCount: getSortedTasks().length,
                        itemBuilder: (context, index) {
                          final sortedTasks = getSortedTasks();
                          final task = sortedTasks[index];
                          final deadline = task['deadline'];
                          final source = task['source'] ?? '';
                          final isCompleted = task['alert_status'] == 'completed';
                          
                          // Check if this is the first completed task to show a separator
                          bool showHeader = false;
                          if (isCompleted && index > 0) {
                            final previousItemIsCompleted = sortedTasks[index - 1]['alert_status'] == 'completed';
                            if (!previousItemIsCompleted) {
                              showHeader = true;
                            }
                          } else if (isCompleted && index == 0) {
                            showHeader = true; // All tasks are completed
                          }

                          Widget taskContent = Dismissible(
                            key: Key(task['id'].toString()),
                            background: Container(
                              color: Colors.red,
                              alignment: Alignment.centerRight,
                              padding: const EdgeInsets.only(right: 20),
                              child: const Icon(Icons.delete, color: Colors.white),
                            ),
                            direction: DismissDirection.endToStart,
                            onDismissed: (direction) async {
                              await _deleteTask(task['id']);
                            },
                            child: Opacity(
                              opacity: isCompleted ? 0.75 : 1.0,
                              child: Card(
                                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                elevation: isCompleted ? 1 : 3,
                                color: isCompleted ? (Theme.of(context).brightness == Brightness.dark ? Colors.grey[900]?.withOpacity(0.5) : Colors.grey[100]) : null,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                  side: BorderSide(
                                    color: isCompleted ? Colors.grey.withOpacity(0.3) : getUrgencyColor(deadline),
                                    width: 2,
                                  ),
                                ),
                                child: ListTile(
                                  leading: Checkbox(
                                    value: isCompleted,
                                    onChanged: (bool? value) async {
                                      if (value == true) {
                                        await _markTaskComplete(task['id']);
                                      } else {
                                        // Optional: Allow unsetting if backend supports it
                                      }
                                    },
                                    shape: const CircleBorder(),
                                  ),
                                  title: Text(
                                    task['summary'] ?? '',
                                    style: TextStyle(
                                      fontWeight: isCompleted ? FontWeight.normal : FontWeight.bold,
                                      fontSize: 16,
                                      decoration: isCompleted ? TextDecoration.lineThrough : null,
                                      color: isCompleted ? Colors.grey[600] : null,
                                    ),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const SizedBox(height: 4),
                                      Row(
                                        children: [
                                          Icon(
                                            getSourceIcon(source),
                                            size: 16,
                                            color: isCompleted ? Colors.grey : getUrgencyColor(deadline),
                                          ),
                                          const SizedBox(width: 4),
                                          Text(
                                            getRelativeTime(deadline),
                                            style: TextStyle(
                                              color: isCompleted ? Colors.grey : getUrgencyColor(deadline),
                                              fontWeight: isCompleted ? FontWeight.normal : FontWeight.w600,
                                              fontSize: 14,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                  isThreeLine: false,
                                  trailing: IconButton(
                                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                                    onPressed: () async {
                                       await _deleteTask(task['id']);
                                    },
                                  ),
                                ),
                              ),
                            ),
                          );

                          if (showHeader) {
                            return Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Padding(
                                  padding: EdgeInsets.fromLTRB(16, 20, 16, 8),
                                  child: Row(
                                    children: [
                                      Icon(Icons.check_circle_outline, size: 20, color: Colors.grey),
                                      SizedBox(width: 8),
                                      Text(
                                        'COMPLETED TASKS',
                                        style: TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.grey,
                                          letterSpacing: 1.2,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                taskContent,
                              ],
                            );
                          }
                          return taskContent;
                        },
                      ),
          ),
          
          // Chat overlay popup
          if (_showChatOverlay)
            Positioned(
              left: 10,
              right: 10,
              // Adjust bottom position based on keyboard height
              bottom: MediaQuery.of(context).viewInsets.bottom > 0 
                  ? MediaQuery.of(context).viewInsets.bottom + 10 
                  : 90,
              child: ChatOverlayWidget(
                onClose: () => setState(() => _showChatOverlay = false),
              ),
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => setState(() => _showChatOverlay = !_showChatOverlay),
        backgroundColor: Colors.deepPurple,
        icon: Icon(_showChatOverlay ? Icons.close : Icons.chat_bubble_outline),
        label: Text(_showChatOverlay ? 'Close Chat' : 'Chat with Groq AI'),
        tooltip: 'Ask questions about your deadlines',
      ),
    );
  }
}

// Chat overlay widget that appears as a popup
class ChatOverlayWidget extends StatefulWidget {
  final VoidCallback onClose;
  
  const ChatOverlayWidget({super.key, required this.onClose});

  @override
  State<ChatOverlayWidget> createState() => _ChatOverlayWidgetState();
}

class _ChatOverlayWidgetState extends State<ChatOverlayWidget> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    // Add welcome message
    _messages.add(ChatMessage(
      text: "Hi! I'm Groq AI. Ask me about your deadlines! 🤖",
      isUser: false,
      timestamp: DateTime.now(),
    ));
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    // Add user message
    setState(() {
      _messages.add(ChatMessage(
        text: text,
        isUser: true,
        timestamp: DateTime.now(),
      ));
      _isLoading = true;
    });

    _messageController.clear();
    
    // Auto-scroll to bottom
    Future.delayed(const Duration(milliseconds: 100), () {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });

    try {
      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://127.0.0.1:8000';
      final response = await http.post(
        Uri.parse('$backendUrl/chat?question=${Uri.encodeComponent(text)}'),
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Chat timeout - please check your internet connection');
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _messages.add(ChatMessage(
            text: data['answer'] ?? 'No response',
            isUser: false,
            timestamp: DateTime.now(),
            provider: data['provider'],
          ));
          _isLoading = false;
        });
      } else {
        setState(() {
          _messages.add(ChatMessage(
            text: 'Error: Failed to get response',
            isUser: false,
            timestamp: DateTime.now(),
          ));
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: 'Error: $e',
          isUser: false,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
    }
    
    // Auto-scroll after AI response
    Future.delayed(const Duration(milliseconds: 100), () {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    
    // Calculate responsive width (max 400 for larger screens)
    final double overlayWidth = screenSize.width > 450 ? 400 : (screenSize.width - 20);
    
    // Calculate responsive height (make it even smaller to ensure it stays on screen)
    final double overlayHeight = keyboardHeight > 0 
        ? (screenSize.height * 0.3) 
        : (screenSize.height * 0.4);

    return Container(
      width: overlayWidth,
      height: overlayHeight,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              color: Colors.deepPurple,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.smart_toy, color: Colors.white),
                const SizedBox(width: 8),
                const Text(
                  'Chat with Groq AI',
                  style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.white, size: 20),
                  onPressed: widget.onClose,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              ],
            ),
          ),

          // Messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(12),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return CompactChatBubble(message: message);
              },
            ),
          ),

          // Loading
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Row(
                children: [
                  SizedBox(width: 16),
                  SizedBox(
                    width: 12,
                    height: 12,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 8),
                  Text('Thinking...', style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            ),

          // Input
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(16),
                bottomRight: Radius.circular(16),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: 'Ask about deadlines...',
                      hintStyle: const TextStyle(fontSize: 14),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(20)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                    style: const TextStyle(fontSize: 14),
                    onSubmitted: _sendMessage,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: () => _sendMessage(_messageController.text),
                  icon: const Icon(Icons.send, color: Colors.deepPurple),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? provider;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.provider,
  });
}

class CompactChatBubble extends StatelessWidget {
  final ChatMessage message;

  const CompactChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser)
            Container(
              margin: const EdgeInsets.only(right: 6),
              padding: const EdgeInsets.all(6),
              decoration: const BoxDecoration(
                color: Colors.deepPurple,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.smart_toy, color: Colors.white, size: 14),
            ),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: message.isUser ? Colors.blue[100] : Colors.grey[200],
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                message.text,
                style: const TextStyle(fontSize: 13),
              ),
            ),
          ),
          if (message.isUser)
            Container(
              margin: const EdgeInsets.only(left: 6),
              padding: const EdgeInsets.all(6),
              decoration: const BoxDecoration(
                color: Colors.blue,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.person, color: Colors.white, size: 14),
            ),
        ],
      ),
    );
  }
}