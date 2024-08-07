import curses
from typing import Dict, Any
from f1_telemetry.server import get_telemetry


def draw_rpm_bar(win: curses.window, y: int, x: int, rpm: int, max_rpm: int) -> None:
    """
    Draws a RPM bar on the window.

    Args:
        win: The curses window to draw on.
        y: The y-coordinate of the top-left corner of the bar.
        x: The x-coordinate of the top-left corner of the bar.
        rpm: The current RPM value.
        max_rpm: The maximum RPM value.
    """
    bar_length = 30
    bar_fill = int((rpm / max_rpm) * bar_length)

    if rpm >= 12000:
        color = curses.color_pair(4)
    elif rpm >= 10000:
        color = curses.color_pair(3)
    else:
        color = curses.color_pair(2)

    win.addstr(y, x, "[", curses.color_pair(1))
    for i in range(bar_length):
        if i < bar_fill:
            win.addstr(y, x + 1 + i, "|", color)
        else:
            win.addstr(y, x + 1 + i, " ", color)
    win.addstr(y, x + 1 + bar_length, "]", curses.color_pair(1))
    win.addstr(y, x + 1 + bar_length + 2, f"{rpm} RPM", curses.color_pair(1))

def draw_brake_bar(win: curses.window, y: int, x: int, brake: float) -> None:
    """
    Draws a brake bar on the window vertically.

    Args:
        win: The curses window to draw on.
        y: The y-coordinate of the top-left corner of the bar.
        x: The x-coordinate of the top-left corner of the bar.
        brake: The current brake value (0-100).
    """
    bar_height = 10
    bar_width = 2
    bar_fill = int((brake / 100) * bar_height)

    # Ensure there's enough space for the bar
    height, width = win.getmaxyx()
    if y + bar_height >= height or x + bar_width >= width:
        return

    win.addstr(y, x, "Brake:", curses.color_pair(1))
    for i in range(bar_height):
        if i < bar_fill:
            win.addstr(y + bar_height - i - 1, x + 7, "|", curses.color_pair(3))
        else:
            win.addstr(y + bar_height - i - 1, x + 7, " ", curses.color_pair(3))


def draw_accel_bar(win: curses.window, y: int, x: int, throttle: float) -> None:
    """
    Draws a throttle bar on the window vertically.

    Args:
        win: The curses window to draw on.
        y: The y-coordinate of the top-left corner of the bar.
        x: The x-coordinate of the top-left corner of the bar.
        throttle: The current throttle value (0-100).
    """
    bar_height = 10
    bar_width = 2
    bar_fill = int((throttle / 100) * bar_height)

    # Ensure there's enough space for the bar
    height, width = win.getmaxyx()
    if y + bar_height >= height or x + bar_width >= width:
        return

    win.addstr(y, x, "Throttle:", curses.color_pair(1))
    for i in range(bar_height):
        if i < bar_fill:
            win.addstr(y + bar_height - i - 1, x + 10, "|", curses.color_pair(2))
        else:
            win.addstr(y + bar_height - i - 1, x + 10, " ", curses.color_pair(2))


def draw_telemetry_box(stdscr: curses.window, data: Dict[str, Any]) -> bool:
    """
    Draws the telemetry box with various telemetry data on the window.

    Args:
        stdscr: The main curses window.
        data: A dictionary containing telemetry data.

    Returns:
        bool: True if drawing was successful, False otherwise.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    min_width = 75
    min_height = 15
    if width < min_width or height < min_height:
        stdscr.addstr(0, 0, "Terminal too small. Please resize and try again.", curses.color_pair(1))
        stdscr.refresh()
        return False

    box_width = 75
    box_height = 15

    telemetry_win = curses.newwin(box_height, box_width, 1, 2)
    telemetry_win.box()

    engine_speed = data.get("engine_speed", 0)
    gear = data.get("gear", 0)
    engine_rpm = data.get("engine_rpm", 0)
    max_rpm = data.get("max_rpm", 15000)
    tire_temperatures = data.get("tire_temperatures", [0, 0, 0, 0])
    tire_wear = data.get("tire_wear", [0, 0, 0, 0])
    throttle = data.get("throttle", 0)
    g_force = data.get("g_force", 0)
    brake = data.get("brake", 0)
    fuel = round(data.get("fuel", 0), 2)

    telemetry_win.addstr(1, 2, f"Speed: {engine_speed} km/h", curses.color_pair(1))
    telemetry_win.addstr(2, 2, f"Gear: {gear}", curses.color_pair(1))
    draw_rpm_bar(telemetry_win, 3, 2, engine_rpm, max_rpm)

    # Display G-Force and Fuel information above tire data
    telemetry_win.addstr(6, 2, f"G-Force: {g_force}", curses.color_pair(1))
    telemetry_win.addstr(7, 2, f"Fuel: {fuel}%", curses.color_pair(1))
    tire_labels = ["RL", "RR", "FL", "FR"]
    for i, temp in enumerate(tire_temperatures):
        color = curses.color_pair(2) if temp <= 150 else curses.color_pair(5) if temp <= 250 else curses.color_pair(3)
        telemetry_win.addstr(9 + i, 2, f"{tire_labels[i]} Temp: {temp}°C", color)

    for i, damage in enumerate(tire_wear):
        color = curses.color_pair(3) if damage > 75 else curses.color_pair(5) if damage > 50 else curses.color_pair(2)
        telemetry_win.addstr(9 + i, 30, f"{tire_labels[i]} Wear: {damage}%", color)

    # Draw accelerator bar
    draw_accel_bar(telemetry_win, 3, 50, throttle)
    # Draw brake bar
    draw_brake_bar(telemetry_win, 3, 63, brake)


    telemetry_win.refresh()
    return True

def print_telemetry(stdscr: curses.window) -> None:
    """
    Main function to handle telemetry data and update the display.

    Args:
        stdscr: The main curses window.
    """
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(500)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    max_rpm = 15000
    data: Dict[str, Any] = {}
    player_car_index: int | None = None

    motion_data: dict = {}
    status_data: dict = {}
    car_setup_data: dict = {}

    while True:
        for packet_id, packet in get_telemetry():
            if packet_id == 6:
                # Car Telemetry Packet
                player_car_index = packet.header.m_playerCarIndex
                packet_car_telemetry_data = packet.cars_telemetry_data[player_car_index]

                engine_speed = packet_car_telemetry_data.m_speed
                engine_rpm = packet_car_telemetry_data.m_engineRPM
                gear = packet_car_telemetry_data.m_gear
                tire_temperatures = packet_car_telemetry_data.m_tyresSurfaceTemperature
                throttle = packet_car_telemetry_data.m_throttle
                brake = packet_car_telemetry_data.m_brake
                fuel = data.get("fuel", 0)

                data = {
                    "engine_speed": engine_speed,
                    "engine_rpm": engine_rpm,
                    "gear": gear,
                    "max_rpm": max_rpm,
                    "tire_temperatures": tire_temperatures,
                    "throttle": throttle,
                    "brake": brake,
                    "fuel": fuel
                }

                if player_car_index is not None:
                    if player_car_index in motion_data:
                        g_force = motion_data[player_car_index].m_gForceLateral
                        data["g_force"] = g_force
                    if player_car_index in status_data:
                        tire_wear = status_data[player_car_index].m_tyresDamage
                        data["tire_wear"] = tire_wear
                    if player_car_index in car_setup_data:
                        fuel = car_setup_data[player_car_index].m_fuelLoad
                        data["fuel"] = fuel

                if not draw_telemetry_box(stdscr, data):
                    return

            elif packet_id == 0:
                # Motion Packet
                if player_car_index is not None:
                    packet_motion_data = packet.cars_motion_data[player_car_index]
                    motion_data[player_car_index] = packet_motion_data

            elif packet_id == 7:
                # Car Status Packet
                if player_car_index is not None:
                    packet_car_status_data = packet.cars_status_data[player_car_index]
                    status_data[player_car_index] = packet_car_status_data
            
            elif packet_id == 5:
                # Car Setup Data Packet
                if player_car_index is not None:
                    packet_car_setup_data = packet.cars_setup_data[player_car_index]
                    car_setup_data[player_car_index] = packet_car_setup_data

        stdscr.refresh()

        if stdscr.getch() == ord("q"):
            break


def main() -> None:
    """
    Entry point for the application. Initializes curses and starts the telemetry display.
    """
    curses.wrapper(print_telemetry)


if __name__ == "__main__":
    main()
