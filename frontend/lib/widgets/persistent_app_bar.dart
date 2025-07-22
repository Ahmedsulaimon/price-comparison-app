import 'package:flutter/material.dart';

class PersistentAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final int currentIndex;
  final Function(int) onTabTapped;

  const PersistentAppBar({
    super.key,
    required this.title,
    required this.currentIndex,
    required this.onTabTapped,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        AppBar(
           
          title: Text(title, style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold

        ),),
          centerTitle: true,
           backgroundColor: Colors.blueAccent,
          elevation: 0,
        ),
        _buildNavigationBar(),
      ],
    );
  }

  Widget _buildNavigationBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[200],
        border: Border(bottom: BorderSide(color: Colors.grey[300]!)),
      ),
      child: Row(
        children: [
          _buildNavItem(0, 'Home', Icons.home),
          _buildNavItem(1, 'Price Prediction', Icons.trending_up),
        ],
      ),
    );
  }

  Widget _buildNavItem(int index, String text, IconData icon) {
    final isSelected = index == currentIndex;
    return Expanded(
      child: InkWell(
        onTap: () => onTabTapped(index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: isSelected ? Colors.blue : Colors.transparent,
                width: 2,
              ),
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: isSelected ? Colors.blue : Colors.grey),
             
              Text(
                text,
                style: TextStyle(
                  color: isSelected ? Colors.blue : Colors.grey,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(130);
}