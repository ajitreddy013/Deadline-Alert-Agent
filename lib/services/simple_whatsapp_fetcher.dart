import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/deadline.dart';

class SimpleWhatsAppFetcher {
  static const String _prefsKey = 'whatsapp_deadlines';
  static const String _lastFetchKey = 'whatsapp_last_fetch';
  
  // Deadline keywords to search for
  static const List<String> _deadlineKeywords = [
    'deadline',
    'due date',
    'due by',
    'submit by',
    'hand in by',
    'complete by',
    'finish by',
    'end date',
    'cutoff',
    'expires',
    'last date',
    'final date',
    'closing date',
    'assignment due',
    'project due',
    'report due',
    'presentation due',
    'meeting',
    'call',
    'review',
  ];
  
  // Date patterns for extraction
  static final List<RegExp> _datePatterns = [
    RegExp(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})'), // DD/MM/YYYY or MM/DD/YYYY
    RegExp(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{2,4})', caseSensitive: false), // DD Month YYYY
    RegExp(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{2,4})', caseSensitive: false), // Month DD, YYYY
    RegExp(r'(\d{4})-(\d{1,2})-(\d{1,2})'), // YYYY-MM-DD
  ];
  
  // Time patterns
  static final List<RegExp> _timePatterns = [
    RegExp(r'(\d{1,2}):(\d{2})\s*(AM|PM)', caseSensitive: false), // 12-hour format
    RegExp(r'(\d{1,2}):(\d{2})'), // 24-hour format
  ];

  /// Fetch deadlines from WhatsApp using local backup or manual input
  static Future<List<Deadline>> fetchFromWhatsApp({
    String? backupFilePath,
    List<String>? manualMessages,
  }) async {
    try {
      if (backupFilePath != null) {
        // In a real implementation, you'd read the WhatsApp backup file
        // For now, we'll use mock data
        return _getMockWhatsAppDeadlines();
      } else if (manualMessages != null) {
        return _extractDeadlinesFromMessages(manualMessages);
      } else {
        // Default to mock data for demonstration
        return _getMockWhatsAppDeadlines();
      }
    } catch (e) {
      print('Error fetching from WhatsApp: $e');
    }
    
    return [];
  }

  /// Extract deadlines from a list of WhatsApp messages
  static List<Deadline> _extractDeadlinesFromMessages(List<String> messages) {
    List<Deadline> deadlines = [];
    
    for (String message in messages) {
      final extractedDeadlines = _extractDeadlinesFromText(
        message,
        'WhatsApp: Manual Input',
      );
      deadlines.addAll(extractedDeadlines);
    }
    
    return deadlines;
  }

  /// Extract deadlines from text using pattern matching
  static List<Deadline> _extractDeadlinesFromText(String text, String source) {
    List<Deadline> deadlines = [];
    final fullText = text.toLowerCase();
    
    // Check if text contains deadline keywords
    bool hasDeadlineKeyword = _deadlineKeywords.any((keyword) => 
        fullText.contains(keyword.toLowerCase()));
    
    if (!hasDeadlineKeyword) return deadlines;
    
    // Extract dates and times
    for (var datePattern in _datePatterns) {
      final dateMatches = datePattern.allMatches(fullText);
      
      for (var dateMatch in dateMatches) {
        DateTime? deadlineDate = _parseDateFromMatch(dateMatch, fullText);
        
        if (deadlineDate != null) {
          // Look for time in the same sentence or nearby
          TimeOfDay? deadlineTime = _extractTimeFromContext(fullText, dateMatch.start);
          
          // Create deadline
          final deadline = Deadline(
            title: _extractTitleFromText(text),
            description: 'Source: $source\n$text',
            deadline: deadlineTime != null 
                ? DateTime(
                    deadlineDate.year,
                    deadlineDate.month,
                    deadlineDate.day,
                    deadlineTime.hour,
                    deadlineTime.minute,
                  )
                : deadlineDate,
            source: source,
          );
          
          deadlines.add(deadline);
        }
      }
    }
    
    return deadlines;
  }

  /// Parse date from regex match
  static DateTime? _parseDateFromMatch(RegExpMatch match, String text) {
    try {
      final groups = match.groups([1, 2, 3]);
      if (groups.length >= 3) {
        int day = int.parse(groups[0]!);
        int month = int.parse(groups[1]!);
        int year = int.parse(groups[2]!);
        
        // Handle 2-digit years
        if (year < 100) {
          year += 2000;
        }
        
        // Validate date
        if (month >= 1 && month <= 12 && day >= 1 && day <= 31) {
          return DateTime(year, month, day);
        }
      }
    } catch (e) {
      print('Error parsing date: $e');
    }
    
    return null;
  }

  /// Extract time from context around the date
  static TimeOfDay? _extractTimeFromContext(String text, int datePosition) {
    // Look for time patterns within 100 characters of the date
    final start = (datePosition - 50).clamp(0, text.length);
    final end = (datePosition + 50).clamp(0, text.length);
    final context = text.substring(start, end);
    
    for (var timePattern in _timePatterns) {
      final timeMatch = timePattern.firstMatch(context);
      if (timeMatch != null) {
        try {
          int hour = int.parse(timeMatch.group(1)!);
          int minute = int.parse(timeMatch.group(2)!);
          
          // Handle 12-hour format
          if (timeMatch.groupCount >= 3 && timeMatch.group(3) != null) {
            final ampm = timeMatch.group(3)!.toUpperCase();
            if (ampm == 'PM' && hour != 12) hour += 12;
            if (ampm == 'AM' && hour == 12) hour = 0;
          }
          
          // Validate time
          if (hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59) {
            return TimeOfDay(hour: hour, minute: minute);
          }
        } catch (e) {
          print('Error parsing time: $e');
        }
      }
    }
    
    return null;
  }

  /// Extract title from text
  static String _extractTitleFromText(String text) {
    final firstLine = text.split('\n').first.trim();
    return firstLine.length > 50 ? '${firstLine.substring(0, 50)}...' : firstLine;
  }

  /// Mock WhatsApp deadlines for demonstration
  static List<Deadline> _getMockWhatsAppDeadlines() {
    final now = DateTime.now();
    return [
      Deadline(
        title: 'Project Review Meeting',
        description: 'Source: WhatsApp\nTeam meeting to review project progress and discuss next steps',
        deadline: now.add(const Duration(days: 2, hours: 14)),
        source: 'WhatsApp: Team Chat',
      ),
      Deadline(
        title: 'Client Presentation',
        description: 'Source: WhatsApp\nPrepare slides for client presentation on new features',
        deadline: now.add(const Duration(days: 1, hours: 9)),
        source: 'WhatsApp: Client Group',
      ),
      Deadline(
        title: 'Code Review',
        description: 'Source: WhatsApp\nReview pull request for authentication module',
        deadline: now.add(const Duration(hours: 6)),
        source: 'WhatsApp: Dev Team',
      ),
      Deadline(
        title: 'Weekly Standup',
        description: 'Source: WhatsApp\nDaily standup meeting to discuss progress',
        deadline: now.add(const Duration(days: 1, hours: 9)),
        source: 'WhatsApp: Work Group',
      ),
    ];
  }

  /// Save fetched deadlines to local storage
  static Future<void> saveFetchedDeadlines(List<Deadline> deadlines) async {
    final prefs = await SharedPreferences.getInstance();
    final deadlineData = deadlines.map((d) => d.toJson()).toList();
    await prefs.setString(_prefsKey, json.encode(deadlineData));
    await prefs.setString(_lastFetchKey, DateTime.now().toIso8601String());
  }

  /// Load fetched deadlines from local storage
  static Future<List<Deadline>> loadFetchedDeadlines() async {
    final prefs = await SharedPreferences.getInstance();
    final deadlineJson = prefs.getString(_prefsKey);
    
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

  /// Get last fetch time
  static Future<DateTime?> getLastFetchTime() async {
    final prefs = await SharedPreferences.getInstance();
    final lastFetchString = prefs.getString(_lastFetchKey);
    
    if (lastFetchString != null) {
      try {
        return DateTime.parse(lastFetchString);
      } catch (e) {
        print('Error parsing last fetch time: $e');
      }
    }
    
    return null;
  }

  /// Check if auto-fetch is due (every 6 hours)
  static Future<bool> shouldAutoFetch() async {
    final lastFetch = await getLastFetchTime();
    if (lastFetch == null) return true;
    
    final now = DateTime.now();
    final difference = now.difference(lastFetch);
    
    // Auto-fetch every 6 hours
    return difference.inHours >= 6;
  }

  /// Add manual WhatsApp message for deadline extraction
  static Future<List<Deadline>> addManualMessage(String message) async {
    final deadlines = _extractDeadlinesFromText(message, 'WhatsApp: Manual Input');
    
    if (deadlines.isNotEmpty) {
      // Save to local storage
      final existingDeadlines = await loadFetchedDeadlines();
      existingDeadlines.addAll(deadlines);
      await saveFetchedDeadlines(existingDeadlines);
    }
    
    return deadlines;
  }
} 