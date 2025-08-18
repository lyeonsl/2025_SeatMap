import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
//import 'package:web_socket_channel/io.dart';
//import 'package:web_socket_channel/web_socket_channel.dart';

class SeatPage extends StatefulWidget {
  final String roomName;
  //final String socketUrl;

  const SeatPage({super.key, required this.roomName});
  
  @override
  _SeatPageState createState() => _SeatPageState();
}


// 좌석 클래스 (좌석 id, 좌표, 점유 상태)
// 점유 상태; true = occupied, false = empty
class Seat {
  final int id;
  final double x;
  final double y;
  bool occupied;

  Seat({required this.id, required this.x, required this.y, this.occupied = false});
}


class _SeatPageState extends State<SeatPage> {
  //late WebSocketChannel channel;

  final double designWidth = 412;
  final double designHeight = 917;

  // 좌석 리스트
  List<Seat> seats = [
    Seat(id: 1, x: 70, y: 323),
    Seat(id: 2, x: 101, y: 323),
    Seat(id: 3, x: 70, y: 354),
    Seat(id: 4, x: 101, y: 354),
    Seat(id: 5, x: 86, y: 385),
    Seat(id: 6, x: 178, y: 323),
    Seat(id: 7, x: 209, y: 323),
    Seat(id: 8, x: 178, y: 354),
    Seat(id: 9, x: 209, y: 354),
    Seat(id: 10, x: 194, y: 385),
    Seat(id: 11, x: 286, y: 323),
    Seat(id: 12, x: 317, y: 323),
    Seat(id: 13, x: 286, y: 354),
    Seat(id: 14, x: 317, y: 354),
    Seat(id: 15, x: 302, y: 385),
    Seat(id: 16, x: 70, y: 436),
    Seat(id: 17, x: 101, y: 436),
    Seat(id: 18, x: 70, y: 467),
    Seat(id: 19, x: 101, y: 467),
    Seat(id: 20, x: 86, y: 498),
    Seat(id: 21, x: 178, y: 436),
    Seat(id: 22, x: 209, y: 436),
    Seat(id: 23, x: 178, y: 467),
    Seat(id: 24, x: 209, y: 467),
    Seat(id: 25, x: 194, y: 498),
    Seat(id: 26, x: 286, y: 436),
    Seat(id: 27, x: 317, y: 436),
    Seat(id: 28, x: 286, y: 467),
    Seat(id: 29, x: 317, y: 467),
    Seat(id: 30, x: 302, y: 498),
  ];


  // 좌석 색상 반환
  Color getSeatColor(bool occupied) {
    return occupied ? const Color(0x7FFF0000) : Colors.black.withOpacity(0.35);
  }

  // 서버 업데이트 예시 ({ 좌석 id: 점유 상태(true/false) } 형태로 데이터 활용)
  void updateSeatStatus(Map<int, bool> newStatus) {
    setState(() {
      for (var seat in seats) {
        if (newStatus.containsKey(seat.id)) {
          seat.occupied = newStatus[seat.id]!;
        }
      }
    });
  }

  // 서버에서 데이터 받고 updateSeatStatus()
  /*
  @override
  void initState() {
    super.initState();
    channel = IOWebSocketChannel.connect(widget.socketUrl);

    channel.stream.listen((message) {
      final data = json.decode(message);
      if (data is Map<String, dynamic>) {
        final newStatus = <int, bool>{};
        data.forEach((key, value) {
          newStatus[int.parse(key)] = value;
        });
        updateSeatStatus(newStatus);
      }
    });
  }
  */

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF050F83),
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              '명신관 ',
              style: TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontFamily: 'Pretendard',
                fontWeight: FontWeight.w700,
              ),
            ),
            Text(
              widget.roomName,
              style: TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontFamily: 'Pretendard',
                fontWeight: FontWeight.w700,
              ),
            )
          ],
        ),
        iconTheme: IconThemeData(
          color: Colors.white, // ← 뒤로가기 아이콘 색상 흰색으로 변경
        ),
        centerTitle: true, // 가운데 정렬
        elevation: 2, // 아래 그림자
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

              // 네트워크 아이콘 (SVG)
              Positioned(
                left: 319 * screenWidth / designWidth,
                top: 177 * screenHeight / designHeight,
                child: SizedBox(
                  width: 30,
                  height: 30,
                  child: SvgPicture.asset(
                    'assets/icons/network.svg',
                    fit: BoxFit.contain,
                  ),
                ),
              ),

              // 맨 위 두 좌석 (색상 유지)
              Positioned(
                left: 64 * screenWidth / designWidth,
                top: 136 * screenHeight / designHeight,
                child: Container(
                  width: 25 * screenWidth / designWidth,
                  height: 25 * screenHeight / designHeight,
                  decoration: BoxDecoration(color: const Color(0x7FFF0000)),
                ),
              ),
              Positioned(
                left: 64 * screenWidth / designWidth,
                top: 186 * screenHeight / designHeight,
                child: Container(
                  width: 25 * screenWidth / designWidth,
                  height: 25 * screenHeight / designHeight,
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.35),
                  ),
                ),
              ),

              // 좌석 상태 텍스트
              Positioned(
                left: 104 * screenWidth / designWidth,
                top: 137 * screenHeight / designHeight,
                child: Text(
                  '사람 있음 / Occupied (사람)',
                  style: TextStyle(
                    color: Colors.black,
                    fontSize: 20 * screenWidth / designWidth,
                    fontFamily: 'Pretendard',
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ),
              Positioned(
                left: 104 * screenWidth / designWidth,
                top: 187 * screenHeight / designHeight,
                child: Text(
                  '비어 있음 / Empty / Available',
                  style: TextStyle(
                    color: Colors.black,
                    fontSize: 20 * screenWidth / designWidth,
                    fontFamily: 'Pretendard',
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ),

              // 칠판 영역
              Positioned(
                left: 133 * screenWidth / designWidth,
                top: 264 * screenHeight / designHeight,
                child: Container(
                  width: 146 * screenWidth / designWidth,
                  height: 18 * screenHeight / designHeight,
                  decoration: ShapeDecoration(
                    color: Colors.white.withOpacity(0.6),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(9)),
                  ),
                ),
              ),

              // 좌석 (데이터 받아 업데이트)
              ...seats.map(
                    (seat) => Positioned(
                  left: seat.x * screenWidth / designWidth,
                  top: seat.y * screenHeight / designHeight,
                  child: Container(
                    width: 25 * screenWidth / designWidth,
                    height: 25 * screenHeight / designHeight,
                    decoration: BoxDecoration(
                      color: getSeatColor(seat.occupied),
                    ),
                  ),
                ),
              ),

              // 에어컨 알림
              Positioned(
                left: 31 * screenWidth / designWidth,
                top: 706 * screenHeight / designHeight,
                child: Container(
                  width: 350 * screenWidth / designWidth,
                  height: 70 * screenHeight / designHeight,
                  decoration: ShapeDecoration(
                    color: const Color(0xD8050F83),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15),
                    ),
                    shadows: const [
                      BoxShadow(
                        color: Color(0x7F000000),
                        blurRadius: 5,
                        offset: Offset(1, 2),
                      )
                    ],
                  ),
                ),
              ),
              Positioned(
                left: 98 * screenWidth / designWidth,
                top: 723 * screenHeight / designHeight,
                child: Text(
                  '에어컨을 꺼주세요',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 30 * screenWidth / designWidth,
                    fontFamily: 'Pretendard',
                    fontWeight: FontWeight.w500,
                    shadows: [
                      Shadow(
                        offset: Offset(0, 4),
                        blurRadius: 4,
                        color: Color(0x40000000),
                      )
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

class SeatBox extends StatelessWidget {
  final Color color;
  const SeatBox({super.key, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 25,
      height: 25,
      decoration: BoxDecoration(color: color),
    );
  }
}