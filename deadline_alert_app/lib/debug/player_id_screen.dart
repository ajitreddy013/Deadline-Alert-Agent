import 'package:flutter/material.dart';
import 'package:onesignal_flutter/onesignal_flutter.dart';

class PlayerIdScreen extends StatefulWidget {
  const PlayerIdScreen({super.key});

  @override
  State<PlayerIdScreen> createState() => _PlayerIdScreenState();
}

class _PlayerIdScreenState extends State<PlayerIdScreen> {
  String? _playerId;
  String _status = 'Tap refresh to get OneSignal player_id';

  Future<void> _fetchPlayerId() async {
    setState(() {
      _status = 'Fetching...';
    });
    try {
      final id = OneSignal.User.pushSubscription.id;
      setState(() {
        _playerId = id;
        _status = id != null && id.isNotEmpty
            ? 'Retrieved successfully'
            : 'Not available yet (is the device subscribed?)';
      });
    } catch (e) {
      setState(() {
        _status = 'Error: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('OneSignal Player ID')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_status),
            const SizedBox(height: 16),
            SelectableText(_playerId ?? '<none>'),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh'),
                onPressed: _fetchPlayerId,
              ),
            ),
          ],
        ),
      ),
    );
  }
}