import 'package:flutter/material.dart';
import 'package:onesignal_flutter/onesignal_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'debug/player_id_screen.dart';
import 'settings_screen.dart';
import 'dart:async';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await dotenv.load();
    // Initialize OneSignal with the app ID from .env file
    final oneSignalAppId = dotenv.env['ONESIGNAL_APP_ID'];
    if (oneSignalAppId != null) {
      OneSignal.initialize(oneSignalAppId);
    } else {
      print('Warning: ONESIGNAL_APP_ID not found in .env file');
    }
  } catch (e) {
    print('Error loading .env file: $e');
    // Continue without OneSignal initialization
  }
  runApp(const DeadlineAlertApp());
}

class DeadlineAlertApp extends StatelessWidget {
  const DeadlineAlertApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Deadline Alert App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const TaskListScreen(),
      routes: {
        '/debug/player-id': (context) => const PlayerIdScreen(),
        '/settings': (context) => const SettingsScreen(),
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
  bool isLoading = true;
  String error = '';
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    fetchTasks();
    // Auto-refresh the task list periodically to reflect ingest updates
    _pollTimer = Timer.periodic(const Duration(seconds: 10), (_) => fetchTasks());
  }

  Future<void> fetchTasks() async {
    setState(() {
      isLoading = true;
      error = '';
    });
    try {
      // Change the URL to your backend's address if needed
      final response = await http.get(Uri.parse('http://localhost:8000/tasks'));
      if (response.statusCode == 200) {
        setState(() {
          tasks = json.decode(response.body);
          isLoading = false;
        });
      } else {
        setState(() {
          error = 'Failed to load tasks';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Error: $e';
        isLoading = false;
      });
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
        title: const Text('Your Deadlines'),
        actions: [
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
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : error.isNotEmpty
              ? Center(child: Text(error))
              : ListView.builder(
                  itemCount: tasks.length,
                  itemBuilder: (context, index) {
                    final task = tasks[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      child: ListTile(
                        title: Text(task['summary'] ?? ''),
                        subtitle: Text('Due: ${task['deadline'] ?? 'N/A'}\nSource: ${task['source'] ?? ''}'),
                        isThreeLine: true,
                      ),
                    );
                  },
                ),
    );
  }
}