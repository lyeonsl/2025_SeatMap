import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'map.dart';

class SettingsPage extends StatelessWidget {
  final double designWidth = 412;
  final double designHeight = 917;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Color(0xFF050F83), // 남색
        title: Text(
          'Settings',
          style: TextStyle(
            color: Colors.white,
            fontSize: 22,
            fontFamily: 'Pretendard',
            fontWeight: FontWeight.w700,
          ),
        ),
        centerTitle: true, // 가운데 정렬
        elevation: 2, // 아래 그림자
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: Container(
          width: screenWidth,
          height: screenHeight,
          color: Colors.white,
          child: Stack(
            children: [
              // 지도 영역
              Positioned(
                left: 0,
                top: 0,
                width: screenWidth,
                height: screenHeight,
                child: Container(
                  color: Color(0xCCDDDFFF), // 지도 배경
                ),
              ),

              // 하단 흰색 배경 버튼
              Positioned(
                left: 31 * screenWidth / designWidth,
                bottom: 20 * screenHeight / designHeight,
                width: 350 * screenWidth / designWidth,
                height: 80 * screenHeight / designHeight,
                child: Container(
                  decoration: ShapeDecoration(
                    color: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(40),
                    ),
                    shadows: [
                      BoxShadow(
                        color: Color(0x3F000000),
                        blurRadius: 5,
                        offset: Offset(0, 3),
                      )
                    ],
                  ),
                  child: Stack(
                    children: [
                      // 남색 Settings 버튼
                      Positioned(
                        right: 5 * screenWidth / designWidth,
                        top: 5 * screenHeight / designHeight,
                        width: 250 * screenWidth / designWidth,
                        height: 70 * screenHeight / designHeight,
                        child: Container(
                          decoration: ShapeDecoration(
                            color: Color(0xFF050F83),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(40),
                            ),
                          ),
                          child: Center(
                            child: Text(
                              'Settings',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 30 * (screenWidth / designWidth),
                                fontFamily: 'Pretendard',
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ),
                      ),
                      // Home 아이콘 (왼쪽)
                      Positioned(
                        left: 20 * screenWidth / designWidth,
                        top: 20 * screenHeight / designHeight,
                        width: 40 * screenWidth / designWidth,
                        height: 40 * screenHeight / designHeight,
                        child: GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              PageRouteBuilder(
                                pageBuilder: (context, animation, secondaryAnimation) => MapPage(),
                                transitionsBuilder: (context, animation, secondaryAnimation, child) {
                                  return child; // 애니메이션 없음
                                },
                              ),
                            );
                          },
                          child: SvgPicture.asset(
                            'assets/icons/home_black.svg',
                            fit: BoxFit.contain,
                          ),
                        ),
                      ),
                      // Settings 아이콘 (오른쪽)
                      Positioned(
                        right: 20 * screenWidth / designWidth,
                        top: 20 * screenHeight / designHeight,
                        width: 40 * screenWidth / designWidth,
                        height: 40 * screenHeight / designHeight,
                        child: SvgPicture.asset(
                          'assets/icons/settings_white.svg',
                          fit: BoxFit.contain,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
