import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/deadline.dart';

class PersonalDeadlineService {
  static const String _deadlinesKey = 'personal_deadlines';
  static const String _settingsKey = 'app_settings';

  /// Save deadlines to local storage
  static Future<void> saveDeadlines(List<Deadline> deadlines) async {
    final prefs = await SharedPreferences.getInstance();
    final deadlineData = deadlines.map((d) => d.toJson()).toList();
    await prefs.setString(_deadlinesKey, json.encode(deadlineData));
  }

  /// Load deadlines from local storage
  static Future<List<Deadline>> loadDeadlines() async {
    final prefs = await SharedPreferences.getInstance();
    final deadlineJson = prefs.getString(_deadlinesKey);
    
    if (deadlineJson != null) {
      try {
        final deadlineData = json.decode(deadlineJson) as List;
        return deadlineData.map((d) => Deadline.fromJson(d)).toList();
      } catch (e) {
        print('Error loading deadlines: $e');
      }
    }
    
    return [];
  }

  /// Add a new deadline
  static Future<void> addDeadline(Deadline deadline) async {
    final deadlines = await loadDeadlines();
    deadlines.add(deadline);
    deadlines.sort((a, b) => a.deadline.compareTo(b.deadline));
    await saveDeadlines(deadlines);
  }

  /// Update an existing deadline
  static Future<void> updateDeadline(Deadline deadline) async {
    final deadlines = await loadDeadlines();
    final index = deadlines.indexWhere((d) => d.id == deadline.id);
    if (index != -1) {
      deadlines[index] = deadline;
      deadlines.sort((a, b) => a.deadline.compareTo(b.deadline));
      await saveDeadlines(deadlines);
    }
  }

  /// Delete a deadline
  static Future<void> deleteDeadline(String id) async {
    final deadlines = await loadDeadlines();
    deadlines.removeWhere((d) => d.id == id);
    await saveDeadlines(deadlines);
  }

  /// Toggle deadline completion status
  static Future<void> toggleDeadline(String id) async {
    final deadlines = await loadDeadlines();
    final index = deadlines.indexWhere((d) => d.id == id);
    if (index != -1) {
      deadlines[index] = deadlines[index].copyWith(
        isCompleted: !deadlines[index].isCompleted,
      );
      await saveDeadlines(deadlines);
    }
  }

  /// Get deadlines by status
  static Future<List<Deadline>> getDeadlinesByStatus({bool? isCompleted}) async {
    final deadlines = await loadDeadlines();
    if (isCompleted != null) {
      return deadlines.where((d) => d.isCompleted == isCompleted).toList();
    }
    return deadlines;
  }

  /// Get overdue deadlines
  static Future<List<Deadline>> getOverdueDeadlines() async {
    final deadlines = await loadDeadlines();
    final now = DateTime.now();
    return deadlines.where((d) => 
      !d.isCompleted && d.deadline.isBefore(now)
    ).toList();
  }

  /// Get upcoming deadlines (next 7 days)
  static Future<List<Deadline>> getUpcomingDeadlines() async {
    final deadlines = await loadDeadlines();
    final now = DateTime.now();
    final weekFromNow = now.add(const Duration(days: 7));
    
    return deadlines.where((d) => 
      !d.isCompleted && 
      d.deadline.isAfter(now) && 
      d.deadline.isBefore(weekFromNow)
    ).toList();
  }

  /// Save app settings
  static Future<void> saveSettings(Map<String, dynamic> settings) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_settingsKey, json.encode(settings));
  }

  /// Load app settings
  static Future<Map<String, dynamic>> loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    final settingsJson = prefs.getString(_settingsKey);
    
    if (settingsJson != null) {
      try {
        return json.decode(settingsJson) as Map<String, dynamic>;
      } catch (e) {
        print('Error loading settings: $e');
      }
    }
    
    // Default settings
    return {
      'notifications_enabled': true,
      'reminder_hours': 24,
      'theme': 'system',
      'sort_by': 'deadline',
    };
  }

  /// Clear all data
  static Future<void> clearAllData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_deadlinesKey);
    await prefs.remove(_settingsKey);
  }

  /// Export deadlines as JSON
  static Future<String> exportDeadlines() async {
    final deadlines = await loadDeadlines();
    return json.encode(deadlines.map((d) => d.toJson()).toList());
  }

  /// Import deadlines from JSON
  static Future<void> importDeadlines(String jsonData) async {
    try {
      final deadlineData = json.decode(jsonData) as List;
      final deadlines = deadlineData.map((d) => Deadline.fromJson(d)).toList();
      await saveDeadlines(deadlines);
    } catch (e) {
      throw Exception('Invalid JSON format: $e');
    }
  }

  /// Get deadline statistics
  static Future<Map<String, int>> getStatistics() async {
    final deadlines = await loadDeadlines();
    final now = DateTime.now();
    
    int total = deadlines.length;
    int completed = deadlines.where((d) => d.isCompleted).length;
    int pending = total - completed;
    int overdue = deadlines.where((d) => 
      !d.isCompleted && d.deadline.isBefore(now)
    ).length;
    int today = deadlines.where((d) => 
      !d.isCompleted && 
      d.deadline.year == now.year &&
      d.deadline.month == now.month &&
      d.deadline.day == now.day
    ).length;
    
    return {
      'total': total,
      'completed': completed,
      'pending': pending,
      'overdue': overdue,
      'today': today,
    };
  }
} 