import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'models/deadline.dart';
import 'services/personal_deadline_service.dart';
import 'services/simple_email_fetcher.dart';
import 'services/simple_whatsapp_fetcher.dart';

void main() {
  runApp(const DeadlineAlertApp());
}

class DeadlineAlertApp extends StatelessWidget {
  const DeadlineAlertApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Deadline Alert',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6750A4),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      home: const DeadlineHomePage(),
    );
  }
}



class DeadlineHomePage extends StatefulWidget {
  const DeadlineHomePage({super.key});

  @override
  State<DeadlineHomePage> createState() => _DeadlineHomePageState();
}

class _DeadlineHomePageState extends State<DeadlineHomePage> {
  final List<Deadline> _deadlines = [];
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  DateTime? _selectedDate;
  TimeOfDay? _selectedTime;
  bool _isLoading = false;
  String _currentFilter = 'all'; // all, pending, completed, overdue, today
  bool _autoFetchEnabled = true;
  String? _emailAddress;
  String? _emailPassword;

  @override
  void initState() {
    super.initState();
    _loadDeadlines();
    _loadSettings();
    _checkAutoFetch();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _loadDeadlines() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final deadlines = await PersonalDeadlineService.loadDeadlines();
      setState(() {
        _deadlines.clear();
        _deadlines.addAll(deadlines);
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading deadlines: $e')),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _loadSettings() async {
    try {
      final settings = await PersonalDeadlineService.loadSettings();
      setState(() {
        _emailAddress = settings['email_address'];
        _emailPassword = settings['email_password'];
        _autoFetchEnabled = settings['auto_fetch_enabled'] ?? true;
      });
    } catch (e) {
      print('Error loading settings: $e');
    }
  }

  Future<void> _checkAutoFetch() async {
    if (!_autoFetchEnabled) return;
    
    final shouldFetchEmail = await SimpleEmailFetcher.shouldAutoFetch();
    final shouldFetchWhatsApp = await SimpleWhatsAppFetcher.shouldAutoFetch();
    
    if (shouldFetchEmail || shouldFetchWhatsApp) {
      await _performAutoFetch();
    }
  }

  Future<void> _performAutoFetch() async {
    setState(() {
      _isLoading = true;
    });

    try {
      List<Deadline> newDeadlines = [];
      
      // Fetch from Email if credentials are available
      if (_emailAddress != null && _emailPassword != null) {
        final emailDeadlines = await SimpleEmailFetcher.fetchFromEmail(
          email: _emailAddress!,
          password: _emailPassword!,
        );
        newDeadlines.addAll(emailDeadlines);
      }
      
      // Always fetch mock WhatsApp data for demonstration
      final whatsappDeadlines = await SimpleWhatsAppFetcher.fetchFromWhatsApp();
      newDeadlines.addAll(whatsappDeadlines);
      
      if (newDeadlines.isNotEmpty) {
        // Add new deadlines to existing ones
        for (var deadline in newDeadlines) {
          await PersonalDeadlineService.addDeadline(deadline);
        }
        
        await _loadDeadlines();
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Auto-fetched ${newDeadlines.length} new deadlines!'),
              backgroundColor: Colors.green,
            ),
          );
        }
      }
      
      // Save fetch time
      await SimpleEmailFetcher.saveFetchedDeadlines(newDeadlines);
      await SimpleWhatsAppFetcher.saveFetchedDeadlines(newDeadlines);
      
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Auto-fetch error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _addDeadline() async {
    if (_formKey.currentState!.validate() && _selectedDate != null && _selectedTime != null) {
      final deadline = Deadline(
        title: _titleController.text,
        description: _descriptionController.text,
        deadline: DateTime(
          _selectedDate!.year,
          _selectedDate!.month,
          _selectedDate!.day,
          _selectedTime!.hour,
          _selectedTime!.minute,
        ),
      );

      try {
        await PersonalDeadlineService.addDeadline(deadline);
        await _loadDeadlines();
        
        _titleController.clear();
        _descriptionController.clear();
        _selectedDate = null;
        _selectedTime = null;
        Navigator.of(context).pop();
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Deadline added successfully!')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error adding deadline: $e')),
          );
        }
      }
    }
  }

  Future<void> _toggleDeadline(String id) async {
    try {
      await PersonalDeadlineService.toggleDeadline(id);
      await _loadDeadlines();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error updating deadline: $e')),
        );
      }
    }
  }

  Future<void> _deleteDeadline(String id) async {
    try {
      await PersonalDeadlineService.deleteDeadline(id);
      await _loadDeadlines();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Deadline deleted successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting deadline: $e')),
        );
      }
    }
  }

  Future<void> _showStatistics() async {
    try {
      final stats = await PersonalDeadlineService.getStatistics();
      
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Deadline Statistics'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildStatRow('Total Deadlines', stats['total'] ?? 0, Colors.blue),
                _buildStatRow('Completed', stats['completed'] ?? 0, Colors.green),
                _buildStatRow('Pending', stats['pending'] ?? 0, Colors.orange),
                _buildStatRow('Overdue', stats['overdue'] ?? 0, Colors.red),
                _buildStatRow('Due Today', stats['today'] ?? 0, Colors.purple),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Close'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading statistics: $e')),
        );
      }
    }
  }

  Widget _buildStatRow(String label, int value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16)),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              value.toString(),
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter Deadlines'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildFilterOption('all', 'All Deadlines'),
            _buildFilterOption('pending', 'Pending Only'),
            _buildFilterOption('completed', 'Completed Only'),
            _buildFilterOption('overdue', 'Overdue Only'),
            _buildFilterOption('today', 'Due Today'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  void _showSettingsDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Settings'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SwitchListTile(
              title: const Text('Auto-fetch from Email & WhatsApp'),
              subtitle: const Text('Automatically fetch deadlines every 6 hours'),
              value: _autoFetchEnabled,
              onChanged: (value) {
                setState(() {
                  _autoFetchEnabled = value;
                });
              },
            ),
            const Divider(),
            ListTile(
              title: const Text('Manual Fetch'),
              subtitle: const Text('Fetch deadlines now'),
              leading: const Icon(Icons.refresh),
              onTap: () {
                Navigator.of(context).pop();
                _performAutoFetch();
              },
            ),
            ListTile(
              title: const Text('Setup Email Integration'),
              subtitle: const Text('Connect your email account (IMAP)'),
              leading: const Icon(Icons.email),
              onTap: () {
                Navigator.of(context).pop();
                _showEmailSetupDialog();
              },
            ),
            ListTile(
              title: const Text('Add WhatsApp Message'),
              subtitle: const Text('Manually add WhatsApp messages'),
              leading: const Icon(Icons.chat),
              onTap: () {
                Navigator.of(context).pop();
                _showWhatsAppMessageDialog();
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showEmailSetupDialog() {
    final emailController = TextEditingController(text: _emailAddress);
    final passwordController = TextEditingController(text: _emailPassword);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Email Integration'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Show current status
            if (_emailAddress != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green.shade600, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Email configured: ${_emailAddress!.split('@')[0]}@***',
                        style: TextStyle(
                          color: Colors.green.shade700,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            const Text(
              'Connect your email account using IMAP:\n\n'
              '• Gmail: imap.gmail.com:993\n'
              '• Outlook: outlook.office365.com:993\n'
              '• Yahoo: imap.mail.yahoo.com:993\n\n'
              'Note: Enable "Less secure app access" for Gmail',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(
                labelText: 'Email Address',
                border: OutlineInputBorder(),
                hintText: 'your.email@gmail.com',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: passwordController,
              decoration: const InputDecoration(
                labelText: 'Password',
                border: OutlineInputBorder(),
                hintText: 'Enter your email password',
              ),
              obscureText: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          if (_emailAddress != null)
            TextButton(
              onPressed: () => _showEmailStatusDialog(),
              child: const Text('Check Status'),
            ),
          ElevatedButton(
            onPressed: () async {
              setState(() {
                _emailAddress = emailController.text.isNotEmpty 
                    ? emailController.text 
                    : null;
                _emailPassword = passwordController.text.isNotEmpty 
                    ? passwordController.text 
                    : null;
              });
              
              // Save settings
              await PersonalDeadlineService.saveSettings({
                'email_address': _emailAddress,
                'email_password': _emailPassword,
                'auto_fetch_enabled': _autoFetchEnabled,
              });
              
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Email integration updated!')),
              );
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showEmailStatusDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Email Integration Status'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Email Address: ${_emailAddress ?? "Not configured"}'),
            const SizedBox(height: 8),
            Text('Password: ${_emailPassword != null ? "Configured" : "Not configured"}'),
            const SizedBox(height: 8),
            Text('Auto-fetch: ${_autoFetchEnabled ? "Enabled" : "Disabled"}'),
            const SizedBox(height: 16),
            const Text(
              'The app will automatically fetch deadlines from your emails every 6 hours when auto-fetch is enabled.',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showWhatsAppMessageDialog() {
    final messageController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add WhatsApp Message'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Paste a WhatsApp message containing a deadline:\n\n'
              'Example: "Team meeting tomorrow at 2 PM"\n'
              'Example: "Project due on 15/12/2024"\n\n'
              'The app will automatically extract deadlines.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: messageController,
              decoration: const InputDecoration(
                labelText: 'WhatsApp Message',
                border: OutlineInputBorder(),
                hintText: 'Paste your WhatsApp message here...',
              ),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (messageController.text.isNotEmpty) {
                final deadlines = await SimpleWhatsAppFetcher.addManualMessage(
                  messageController.text,
                );
                
                if (deadlines.isNotEmpty) {
                  // Add to main deadline list
                  for (var deadline in deadlines) {
                    await PersonalDeadlineService.addDeadline(deadline);
                  }
                  
                  await _loadDeadlines();
                  
                  Navigator.of(context).pop();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Extracted ${deadlines.length} deadline(s)!'),
                      backgroundColor: Colors.green,
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('No deadlines found in the message'),
                      backgroundColor: Colors.orange,
                    ),
                  );
                }
              }
            },
            child: const Text('Extract Deadlines'),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterOption(String value, String label) {
    return ListTile(
      title: Text(label),
      leading: Radio<String>(
        value: value,
        groupValue: _currentFilter,
        onChanged: (newValue) {
          setState(() {
            _currentFilter = newValue!;
          });
          Navigator.of(context).pop();
        },
      ),
    );
  }

  String _getTimeRemaining(DateTime deadline) {
    final now = DateTime.now();
    final difference = deadline.difference(now);

    if (difference.isNegative) {
      return 'Overdue';
    }

    final days = difference.inDays;
    final hours = difference.inHours % 24;
    final minutes = difference.inMinutes % 60;

    if (days > 0) {
      return '$days days, $hours hours';
    } else if (hours > 0) {
      return '$hours hours, $minutes minutes';
    } else {
      return '$minutes minutes';
    }
  }

  Color _getPriorityColor(DateTime deadline) {
    final now = DateTime.now();
    final difference = deadline.difference(now);

    if (difference.isNegative) {
      return Colors.red;
    } else if (difference.inDays < 1) {
      return Colors.orange;
    } else if (difference.inDays < 3) {
      return Colors.yellow.shade700;
    } else {
      return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    
    List<Deadline> filteredDeadlines = _deadlines.where((deadline) {
      switch (_currentFilter) {
        case 'pending':
          return !deadline.isCompleted;
        case 'completed':
          return deadline.isCompleted;
        case 'overdue':
          return !deadline.isCompleted && deadline.deadline.isBefore(now);
        case 'today':
          final deadlineDate = DateTime(
            deadline.deadline.year,
            deadline.deadline.month,
            deadline.deadline.day,
          );
          return !deadline.isCompleted && deadlineDate.isAtSameMomentAs(today);
        default:
          return true; // 'all'
      }
    }).toList();

    final pendingDeadlines = filteredDeadlines.where((d) => !d.isCompleted).toList();
    final completedDeadlines = filteredDeadlines.where((d) => d.isCompleted).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Deadline Alert',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        elevation: 0,
        actions: [
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            )
          else ...[
            IconButton(
              icon: const Icon(Icons.filter_list),
              onPressed: _showFilterDialog,
              tooltip: 'Filter Deadlines',
            ),
            IconButton(
              icon: const Icon(Icons.analytics),
              onPressed: _showStatistics,
              tooltip: 'View Statistics',
            ),
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: _showSettingsDialog,
              tooltip: 'Settings & Auto-fetch',
            ),
          ],
        ],
      ),
      body: filteredDeadlines.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    _currentFilter == 'all' ? Icons.schedule : Icons.filter_list,
                    size: 80,
                    color: Colors.grey.shade400,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _currentFilter == 'all' 
                        ? 'No deadlines yet'
                        : 'No ${_currentFilter} deadlines',
                    style: TextStyle(
                      fontSize: 20,
                      color: Colors.grey.shade600,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _currentFilter == 'all'
                        ? 'Tap the + button to add your first deadline'
                        : 'Try changing the filter or add new deadlines',
                    style: TextStyle(
                      color: Colors.grey.shade500,
                    ),
                  ),
                ],
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (_currentFilter == 'all') ...[
                  if (pendingDeadlines.isNotEmpty) ...[
                    Text(
                      'Pending (${pendingDeadlines.length})',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...pendingDeadlines.map((deadline) => _buildDeadlineCard(deadline)),
                    const SizedBox(height: 24),
                  ],
                  if (completedDeadlines.isNotEmpty) ...[
                    Text(
                      'Completed (${completedDeadlines.length})',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...completedDeadlines.map((deadline) => _buildDeadlineCard(deadline)),
                  ],
                ] else ...[
                  ...filteredDeadlines.map((deadline) => _buildDeadlineCard(deadline)),
                ],
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddDeadlineDialog(),
        label: const Text('Add Deadline'),
        icon: const Icon(Icons.add),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Theme.of(context).colorScheme.onPrimary,
      ),
    );
  }

  Widget _buildDeadlineCard(Deadline deadline) {
    final isOverdue = deadline.deadline.isBefore(DateTime.now()) && !deadline.isCompleted;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: deadline.isCompleted 
              ? Colors.grey.shade300 
              : _getPriorityColor(deadline.deadline),
          child: Icon(
            deadline.isCompleted ? Icons.check : Icons.schedule,
            color: deadline.isCompleted ? Colors.grey.shade600 : Colors.white,
          ),
        ),
        title: Text(
          deadline.title,
          style: TextStyle(
            decoration: deadline.isCompleted ? TextDecoration.lineThrough : null,
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (deadline.description.isNotEmpty) ...[
              Text(
                deadline.description,
                style: TextStyle(
                  decoration: deadline.isCompleted ? TextDecoration.lineThrough : null,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 4),
            ],
            if (deadline.source != null) ...[
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: deadline.source!.contains('Gmail') 
                      ? Colors.blue.shade100 
                      : Colors.green.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  deadline.source!,
                  style: TextStyle(
                    fontSize: 10,
                    color: deadline.source!.contains('Gmail') 
                        ? Colors.blue.shade700 
                        : Colors.green.shade700,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              const SizedBox(height: 4),
            ],
            Row(
              children: [
                Icon(
                  Icons.access_time,
                  size: 14,
                  color: isOverdue ? Colors.red : Colors.grey.shade600,
                ),
                const SizedBox(width: 4),
                Text(
                  DateFormat('MMM dd, yyyy - HH:mm').format(deadline.deadline),
                  style: TextStyle(
                    fontSize: 12,
                    color: isOverdue ? Colors.red : Colors.grey.shade600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            if (!deadline.isCompleted) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(
                    Icons.timer,
                    size: 14,
                    color: _getPriorityColor(deadline.deadline),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _getTimeRemaining(deadline.deadline),
                    style: TextStyle(
                      fontSize: 12,
                      color: _getPriorityColor(deadline.deadline),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Icon(
                deadline.isCompleted ? Icons.undo : Icons.check_circle_outline,
                color: deadline.isCompleted ? Colors.orange : Colors.green,
              ),
              onPressed: () => _toggleDeadline(deadline.id),
            ),
            IconButton(
              icon: const Icon(Icons.delete_outline, color: Colors.red),
              onPressed: () => _deleteDeadline(deadline.id),
            ),
          ],
        ),
      ),
    );
  }

  void _showAddDeadlineDialog() {
    _selectedDate = null;
    _selectedTime = null;
    _titleController.clear();
    _descriptionController.clear();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add New Deadline'),
        content: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: _titleController,
                  decoration: const InputDecoration(
                    labelText: 'Title',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter a title';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Description (optional)',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ListTile(
                        title: const Text('Date'),
                        subtitle: Text(
                          _selectedDate == null
                              ? 'Select date'
                              : DateFormat('MMM dd, yyyy').format(_selectedDate!),
                        ),
                        onTap: () async {
                          final date = await showDatePicker(
                            context: context,
                            initialDate: DateTime.now(),
                            firstDate: DateTime.now(),
                            lastDate: DateTime.now().add(const Duration(days: 365)),
                          );
                          if (date != null) {
                            setState(() {
                              _selectedDate = date;
                            });
                          }
                        },
                      ),
                    ),
                    Expanded(
                      child: ListTile(
                        title: const Text('Time'),
                        subtitle: Text(
                          _selectedTime == null
                              ? 'Select time'
                              : _selectedTime!.format(context),
                        ),
                        onTap: () async {
                          final time = await showTimePicker(
                            context: context,
                            initialTime: TimeOfDay.now(),
                          );
                          if (time != null) {
                            setState(() {
                              _selectedTime = time;
                            });
                          }
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: _addDeadline,
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}
