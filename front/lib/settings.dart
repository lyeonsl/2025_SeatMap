import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'map.dart';

class SettingsPage extends StatefulWidget {
  @override
  _SettingsPageState createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final double designWidth = 412;
  final double designHeight = 917;

  String name = '눈송이';
  String studentId = '2300000';
  String major = '인공지능공학부';

  @override
  void initState() {
    super.initState();
    _loadSavedData();
  }

  // 데이터 불러오기
  void _loadSavedData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      name = prefs.getString('name') ?? '눈송이';
      studentId = prefs.getString('studentId') ?? '2300000';
      major = prefs.getString('major') ?? '인공지능공학부';
    });
  }

  //데이터 저장
  void saveData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('name', name);
    await prefs.setString('studentId', studentId);
    await prefs.setString('major', major);
  }

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

              // 정보 수정 창
              Positioned(
                left: 41 * screenWidth / designWidth,
                top: 46 * screenHeight / designHeight,
                child: Container(
                    width: 330 * screenWidth / designWidth,
                    height: 219 * screenHeight / designHeight,
                    decoration: ShapeDecoration(
                      color: Colors.white.withOpacity(0.6),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    child: Stack(
                      children: [
                        // 정보 텍스트
                        Positioned(
                          left: 27 * screenWidth / designWidth,
                          top: 20 * screenHeight / designHeight,
                          child: Text(
                            '이름: $name',
                            style: TextStyle(
                              color: Colors.black,
                              fontSize: 20 * screenWidth / designWidth,
                              fontFamily: 'Pretendard',
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        Positioned(
                          left: 27 * screenWidth / designWidth,
                          top: 57 * screenHeight / designHeight,
                          child: Text(
                            '학번: $studentId',
                            style: TextStyle(
                              color: Colors.black,
                              fontSize: 20 * screenWidth / designWidth,
                              fontFamily: 'Pretendard',
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        Positioned(
                          left: 27 * screenWidth / designWidth,
                          top: 94 * screenHeight / designHeight,
                          child: Text(
                            '학과: $major',
                            style: TextStyle(
                              color: Colors.black,
                              fontSize: 20 * screenWidth / designWidth,
                              fontFamily: 'Pretendard',
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),

                        //정보 수정 버튼
                        Positioned(
                            right: 10 * screenWidth / designWidth,
                            bottom: 10 * screenHeight / designHeight,
                            child: GestureDetector(
                              onTap: () {
                                _showEditDialog();
                              },
                              child: Container(
                                width: 95 * screenWidth / designWidth,
                                height: 32 * screenHeight / designHeight,
                                decoration: ShapeDecoration(
                                  color: Colors.white,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  shadows: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.1),
                                      blurRadius: 4,
                                      offset: Offset(1, 1),
                                    )
                                  ],
                                ),
                                child: Center(
                                  child: Text(
                                    "정보 수정",
                                    style: TextStyle(
                                      color: Colors.black,
                                      fontSize: 20 * screenWidth / designWidth,
                                      fontFamily: 'Pretendard',
                                      fontWeight: FontWeight.w400,
                                    ),
                                  ),
                                ),
                              ),
                            )
                        )
                      ],
                    )
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

  void _showEditDialog() {
    final nameController = TextEditingController(text: name);
    final idController = TextEditingController(text: studentId);
    final majorController = TextEditingController(text: major);

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('정보 수정'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                keyboardType: TextInputType.text,
                textInputAction: TextInputAction.done,
                decoration: InputDecoration(labelText: '이름'),
              ),
              TextField(
                controller: idController,
                keyboardType: TextInputType.text,
                textInputAction: TextInputAction.done,
                decoration: InputDecoration(labelText: '학번'),
              ),
              TextField(
                controller: majorController,
                keyboardType: TextInputType.text,
                textInputAction: TextInputAction.done,
                decoration: InputDecoration(labelText: '학과'),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () {
              Navigator.of(context).pop();
            },
              child: Text('취소'),
            ),
            TextButton(onPressed: () {
              setState(() {
                name = nameController.text;
                studentId = idController.text;
                major = majorController.text;
              });
              saveData();
              Navigator.of(context).pop();
            },
                child: Text('확인'))
          ],
        );
      },
    );
  }
}