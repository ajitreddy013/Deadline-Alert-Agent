import 'package:flutter/material.dart';
import 'main.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:url_launcher/url_launcher.dart';
import 'dart:io';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late final GoogleSignIn _googleSignIn;
  List accounts = [];
  bool isLoading = true;
  bool _isInitStarted = false;

  @override
  void initState() {
    super.initState();
    final clientId = dotenv.env['GOOGLE_CLIENT_ID'];
    print("Initializing GoogleSignIn with ClientID: $clientId");
    
    _googleSignIn = GoogleSignIn(
      clientId: clientId,
      serverClientId: kIsWeb ? null : clientId,
      scopes: [
        'email',
        'profile',
        'https://www.googleapis.com/auth/gmail.readonly',
      ],
      forceCodeForRefreshToken: true,
    );

    _googleSignIn.onCurrentUserChanged.listen((GoogleSignInAccount? account) {
      if (account != null) {
        print("DEBUG: Stream detected user: ${account.email}");
        print("DEBUG: Stream Auth Code: ${account.serverAuthCode}");
        if (account.serverAuthCode != null) {
          _sendCodeToBackend(account);
        } else {
          print("DEBUG: Stream detected user BUT serverAuthCode is NULL");
        }
      } else {
        print("DEBUG: Stream detected NULL account (signed out?)");
      }
    });

    if (kIsWeb) {
      _googleSignIn.canAccessScopes(['email']).then((_) {
        setState(() => _isInitStarted = true);
      }).catchError((e) {
        print("Initial scope check failed (expected): $e");
        setState(() => _isInitStarted = true);
      });
    }

    fetchAccounts();
  }

  Future<void> _sendCodeToBackend(GoogleSignInAccount user) async {
    print("DEBUG: Sending code to backend for ${user.email}...");
    try {
      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
      final response = await http.post(
        Uri.parse('$backendUrl/auth/google/exchange'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'code': user.serverAuthCode,
          'email': user.email,
          'account_name': user.displayName ?? 'Personal',
        }),
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Connection timeout - please check your internet connection');
        },
      );
      
      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Successfully connected ${user.email}')),
          );
        }
        fetchAccounts();
      } else {
        _showErrorDialog('Backend Error', response.body);
      }
    } catch (e) {
      print("DEBUG: Exchange error: $e");
    }
  }

  Future<void> fetchAccounts() async {
    setState(() => isLoading = true);
    try {
      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
      final response = await http.get(
        Uri.parse('$backendUrl/accounts'),
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Connection timeout - please check your internet connection');
        },
      );
      if (response.statusCode == 200) {
        setState(() {
          accounts = json.decode(response.body);
          isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error fetching accounts: $e');
      setState(() => isLoading = false);
    }
  }

  Future<void> _handleSignIn() async {
    try {
      final GoogleSignInAccount? user = await _googleSignIn.signIn();
      if (user != null && user.serverAuthCode != null) {
        await _sendCodeToBackend(user);
      } else if (user != null) {
        _showErrorDialog(
          'One more step...', 
          'Google requires explicit confirmation. Please use the button at the bottom labeled "Sign in with Google" to complete the connection.'
        );
      }
    } catch (error) {
      print('DEBUG: Sign-in error: $error');
      _showErrorDialog('Connection Error', error.toString());
    }
  }

  void _showErrorDialog(String title, String message) {
    if (!mounted) return;
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('OK')),
        ],
      ),
    );
  }

  Future<void> _deleteAccount(int id) async {
    try {
      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
      final response = await http.delete(
        Uri.parse('$backendUrl/accounts/$id'),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Connection timeout - please check your internet connection');
        },
      );
      if (response.statusCode == 200) {
        fetchAccounts();
      }
    } catch (e) {
      debugPrint('Error deleting account: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings & Accounts'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Appearance',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            ValueListenableBuilder<ThemeMode>(
              valueListenable: themeNotifier,
              builder: (context, currentMode, _) {
                return Card(
                  child: Column(
                    children: [
                      RadioListTile<ThemeMode>(
                        title: const Text('🌟 System Default'),
                        value: ThemeMode.system,
                        groupValue: currentMode,
                        onChanged: (mode) => themeNotifier.value = mode!,
                      ),
                      RadioListTile<ThemeMode>(
                        title: const Text('☀️ Light Mode'),
                        value: ThemeMode.light,
                        groupValue: currentMode,
                        onChanged: (mode) => themeNotifier.value = mode!,
                      ),
                      RadioListTile<ThemeMode>(
                        title: const Text('🌙 Dark Mode'),
                        value: ThemeMode.dark,
                        groupValue: currentMode,
                        onChanged: (mode) => themeNotifier.value = mode!,
                      ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 24),
            const Text(
              'Connected Accounts',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : accounts.isEmpty
                      ? const Center(child: Text('No accounts connected yet.'))
                      : ListView.builder(
                          itemCount: accounts.length,
                          itemBuilder: (context, index) {
                            final account = accounts[index];
                            return Card(
                              child: ListTile(
                                leading: const Icon(Icons.email, color: Colors.blue),
                                title: Text(account['email']),
                                subtitle: const Text('Status: Connected'),
                                trailing: IconButton(
                                  icon: const Icon(Icons.delete, color: Colors.red),
                                  onPressed: () => _deleteAccount(account['id']),
                                ),
                              ),
                            );
                          },
                        ),
            ),
            const Divider(),
            Center(
              child: Column(
                children: [
                  const Text("Quick Connect (Standard)"),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _handleSignIn,
                    icon: const Icon(Icons.login),
                    label: const Text('Connect Gmail'),
                  ),
                  if (kIsWeb) ...[
                    const SizedBox(height: 24),
                    const Text("Reliable Connection (Recommended for Web)"),
                    const SizedBox(height: 8),
                    const Text("Use the 'Connect via Browser' button below if standard login fails."),
                  ],
                  const SizedBox(height: 24),
                  const Text("Rock-Solid Connection (External Window)"),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: () async {
                      final backendUrl = dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000';
                      final url = Uri.parse('$backendUrl/auth/google/login');
                      try {
                        await launchUrl(url, mode: LaunchMode.externalApplication);
                      } catch (e) {
                        debugPrint('Could not launch $url: $e');
                      }
                    },
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.orange[100], foregroundColor: Colors.orange[900]),
                    icon: const Icon(Icons.open_in_new),
                    label: const Text('Connect via Browser (Safest)'),
                  ),
                  const SizedBox(height: 16),
                  TextButton.icon(
                    onPressed: () async {
                      await _googleSignIn.disconnect();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Session reset.')),
                      );
                    },
                    icon: const Icon(Icons.refresh, size: 16),
                    label: const Text('Reset Session'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                   const Text('System Status', style: TextStyle(fontWeight: FontWeight.bold)),
                   const SizedBox(height: 4),
                   Text('Environment: ${kIsWeb ? 'Web' : 'Native'}', style: const TextStyle(fontSize: 12)),
                   Text('Client ID: ${dotenv.env['GOOGLE_CLIENT_ID']?.substring(0, 10)}...', style: const TextStyle(fontSize: 12)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
