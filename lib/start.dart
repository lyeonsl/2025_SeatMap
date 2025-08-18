import 'package:flutter/material.dart';
import 'dart:async';
import 'map.dart';

class StartPage extends StatefulWidget {
  @override
  _StartPageState createState() => _StartPageState();
}

class _StartPageState extends State<StartPage> {
  @override
  void initState() {
    super.initState();
    // 3초 후 다음 화면으로 이동
    Timer(Duration(seconds: 3), () {
      Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => MapPage()),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    // 화면 크기 가져오기
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      body: SafeArea(
          child: Container(
            width: screenWidth,
            height: screenHeight,
            color: Colors.white,
              child: Stack(
                children: [
                  Align(
                    alignment: Alignment.center, // 화면 중앙
                    child: Container(
                      width: screenWidth * 350 / 412,
                      height: screenHeight * 70 / 917,
                      decoration: ShapeDecoration(
                        color: const Color(0xFF050F83),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(35),
                        ),
                        shadows: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.5),
                            blurRadius: 5,
                            offset: Offset(1, 2),
                          ),
                        ],
                      ),
                      child: Center(
                        child: Text(
                          'SeatMap',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 55 * (screenWidth / 412),
                            fontFamily: 'Pretendard',
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              )

          ),
      ),
    );
  }
}