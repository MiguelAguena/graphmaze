LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY mon_mov_gen IS
    PORT (
        clock, reset : IN STD_LOGIC;
        mon_rom_data : IN STD_LOGIC_VECTOR(27 DOWNTO 0);
        jog_cur, mon_cur : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
        nex_mov : OUT STD_LOGIC_VECTOR(1 DOWNTO 0)
    );
END mon_mov_gen;

ARCHITECTURE behav OF mon_mov_gen IS

    COMPONENT registrador_n IS
        GENERIC (
            CONSTANT N : INTEGER := 8;
            reset_value : NATURAL
        );
        PORT (
            clock : IN STD_LOGIC;
            reset : IN STD_LOGIC;
            load : IN STD_LOGIC;
            D : IN STD_LOGIC_VECTOR (N - 1 DOWNTO 0);
            Q : OUT STD_LOGIC_VECTOR (N - 1 DOWNTO 0)
        );
    END COMPONENT;

    SIGNAL test_mov : STD_LOGIC_VECTOR(1 DOWNTO 0) := (OTHERS => '0');
    SIGNAL test_room, cur_dist, distance_abs : STD_LOGIC_VECTOR(4 DOWNTO 0);
    SIGNAL distance_val : STD_LOGIC_VECTOR(5 DOWNTO 0);
    SIGNAL reg_load, less_than, dif_room : STD_LOGIC;
    SIGNAL u_jog_cur, u_test_room : unsigned(4 DOWNTO 0);
BEGIN
    mov_iterate : PROCESS (clock)
    BEGIN
        IF rising_edge(clock) THEN
            test_mov <= STD_LOGIC_VECTOR(unsigned(test_mov) + to_unsigned(1, 2));
        END IF;
    END PROCESS; -- mov_iterate

    WITH test_mov SELECT test_room <=
        (mon_rom_data(6 DOWNTO 2)) WHEN "00",
        (mon_rom_data(13 DOWNTO 9)) WHEN "01",
        (mon_rom_data(20 DOWNTO 16)) WHEN "10",
        (mon_rom_data(27 DOWNTO 23)) WHEN OTHERS;

    u_jog_cur <= unsigned(jog_cur);
    u_test_room <= unsigned(test_room);
    distance_val <= STD_LOGIC_VECTOR((to_unsigned(0, 1) & u_jog_cur) - (to_unsigned(0, 1) & u_test_room));
    distance_abs <= distance_val(4 DOWNTO 0) WHEN distance_val(5) = '0' ELSE
        STD_LOGIC_VECTOR(unsigned(NOT distance_val(4 DOWNTO 0)) + to_unsigned(1, 5));
    less_than <= '1' WHEN unsigned(distance_abs) <= unsigned(cur_dist) ELSE
        '0';
    dif_room <= '1' WHEN mon_cur /= test_room ELSE
        '0';
    reg_load <= less_than AND dif_room;
    reg_dist : registrador_n GENERIC MAP(5, 31) PORT MAP(clock, reset, reg_load, distance_abs, cur_dist);
    reg_dir : registrador_n GENERIC MAP(2, 0) PORT MAP(clock, reset, reg_load, test_mov, nex_mov);
END behav;