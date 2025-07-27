import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/deadline.dart';

class SimpleEmailFetcher {
  static const String _prefsKey = 'email_deadlines';
  static const String _lastFetchKey = 'email_last_fetch';
  
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

  /// Fetch deadlines from email using IMAP (simplified approach)
  static Future<List<Deadline>> fetchFromEmail({
    required String email,
    required String password,
    String imapServer = 'imap.gmail.com',
    int imapPort = 993,
  }) async {
    try {
      // For demonstration, we'll use mock data
      // In a real implementation, you'd use an IMAP library like 'imap' package
      return _getMockEmailDeadlines();
    } catch (e) {
      print('Error fetching from email: $e');
    }
    
    return [];
  }

  /// Extract deadlines from text using pattern matching
  static List<Deadline> _extractDeadlinesFromText(String subject, String body, String source) {
    List<Deadline> deadlines = [];
    final fullText = '$subject $body'.toLowerCase();
    
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
            title: _extractTitleFromText(subject, body),
            description: 'Source: $source\n${_extractDescriptionFromText(body)}',
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

  /// Extract title from email subject or first line of body
  static String _extractTitleFromText(String subject, String body) {
    if (subject.isNotEmpty) {
      return subject.length > 50 ? '${subject.substring(0, 50)}...' : subject;
    }
    
    final firstLine = body.split('\n').first.trim();
    return firstLine.length > 50 ? '${firstLine.substring(0, 50)}...' : firstLine;
  }

  /// Extract description from body text
  static String _extractDescriptionFromText(String body) {
    final lines = body.split('\n').take(3).join('\n').trim();
    return lines.length > 100 ? '${lines.substring(0, 100)}...' : lines;
  }

  /// Mock email deadlines for demonstration
  static List<Deadline> _getMockEmailDeadlines() {
    final now = DateTime.now();
    return [
      Deadline(
        title: 'Project Submission Deadline',
        description: 'Source: Email\nPlease submit your final project report by the deadline',
        deadline: now.add(const Duration(days: 5, hours: 17)),
        source: 'Email: professor@university.edu',
      ),
      Deadline(
        title: 'Team Meeting',
        description: 'Source: Email\nWeekly team sync meeting to discuss progress',
        deadline: now.add(const Duration(days: 1, hours: 10)),
        source: 'Email: team@company.com',
      ),
      Deadline(
        title: 'Invoice Payment Due',
        description: 'Source: Email\nPlease process the invoice payment by the due date',
        deadline: now.add(const Duration(days: 3, hours: 12)),
        source: 'Email: billing@vendor.com',
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
} 