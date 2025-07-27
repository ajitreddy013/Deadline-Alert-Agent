class Deadline {
  final String title;
  final String description;
  final DateTime deadline;
  final bool isCompleted;
  final String id;
  final String? source;

  Deadline({
    required this.title,
    required this.description,
    required this.deadline,
    this.isCompleted = false,
    String? id,
    this.source,
  }) : id = id ?? DateTime.now().millisecondsSinceEpoch.toString();

  Deadline copyWith({
    String? title,
    String? description,
    DateTime? deadline,
    bool? isCompleted,
    String? source,
  }) {
    return Deadline(
      title: title ?? this.title,
      description: description ?? this.description,
      deadline: deadline ?? this.deadline,
      isCompleted: isCompleted ?? this.isCompleted,
      id: this.id,
      source: source ?? this.source,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'deadline': deadline.toIso8601String(),
      'isCompleted': isCompleted,
      'source': source,
    };
  }

  factory Deadline.fromJson(Map<String, dynamic> json) {
    return Deadline(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      deadline: DateTime.parse(json['deadline'] as String),
      isCompleted: json['isCompleted'] as bool? ?? false,
      source: json['source'] as String?,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Deadline && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'Deadline(id: $id, title: $title, deadline: $deadline, isCompleted: $isCompleted)';
  }
} 