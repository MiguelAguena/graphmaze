LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY data_flux IS
	PORT (
		clock, reset, mode : IN STD_LOGIC;
		dir_btns : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
		next_map_btn : IN STD_LOGIC;
		won : OUT STD_LOGIC;
		lost : OUT STD_LOGIC;
		walls : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
		current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		monster_current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		-- last_move : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
		full_state : OUT STD_LOGIC_VECTOR(14 DOWNTO 0)
	);
END data_flux;

-- full state

-- 15 bits

--	14 .. 12		LAST MOVE
--	11 ..  7		CUR POS
--	6  ..  2		MON POS
--	1  ..  0		MAP

ARCHITECTURE behav OF data_flux IS

	COMPONENT rom_128x20 IS
		PORT (
			enderecoA : IN STD_LOGIC_VECTOR(6 DOWNTO 0);
			enderecoB : IN STD_LOGIC_VECTOR(6 DOWNTO 0);
			dado_saidaA : OUT STD_LOGIC_VECTOR(27 DOWNTO 0);
			dado_saidaB : OUT STD_LOGIC_VECTOR(27 DOWNTO 0)
		);
	END COMPONENT;
	COMPONENT edge_detector IS
		PORT (
			clock : IN STD_LOGIC;
			reset : IN STD_LOGIC;
			sinal : IN STD_LOGIC;
			pulso : OUT STD_LOGIC
		);
	END COMPONENT;

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

	COMPONENT mon_mov_gen IS
		PORT (
			clock, reset : IN STD_LOGIC;
			mon_rom_data : IN STD_LOGIC_VECTOR(27 DOWNTO 0);
			jog_cur, mon_cur : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
			nex_mov : OUT STD_LOGIC_VECTOR(1 DOWNTO 0)
		);
	END COMPONENT;

	SIGNAL jog_room_code : STD_LOGIC_VECTOR(4 DOWNTO 0) := (OTHERS => '0');
	SIGNAL jog_next_room_data : STD_LOGIC_VECTOR(6 DOWNTO 0);

	SIGNAL monster_room_code : STD_LOGIC_VECTOR(4 DOWNTO 0) := "11110";
	SIGNAL monster_next_room : STD_LOGIC_VECTOR(4 DOWNTO 0) := (OTHERS => '0');
	SIGNAL monster_direction : STD_LOGIC_VECTOR(1 DOWNTO 0);

	SIGNAL map_code, next_map : STD_LOGIC_VECTOR(1 DOWNTO 0) := (OTHERS => '0');

	SIGNAL rom_addr_jog, rom_addr_mon : STD_LOGIC_VECTOR(6 DOWNTO 0);
	SIGNAL rom_data_jog, rom_data_mon : STD_LOGIC_VECTOR(27 DOWNTO 0);

	SIGNAL s_lost_v, s_next_lost_v : STD_LOGIC_VECTOR(0 DOWNTO 0);
	SIGNAL room_cnt, map_cnt, btns_or, move_pulse, s_won, s_lost, jog_mon_nex_eq : STD_LOGIC;
	SIGNAL has_door, mov_dir : STD_LOGIC_VECTOR(3 DOWNTO 0);

	SIGNAL continue, crossed_to_mon, crossed_to_jog, crossed_path, crossed : STD_LOGIC := '0';

	SIGNAL cur_move, s_last_move : STD_LOGIC_VECTOR(2 DOWNTO 0);

	SIGNAL reset_or_map, room_cnt_cont, reset_or_play : STD_LOGIC;

BEGIN
	continue <= (NOT(s_won) AND NOT(s_lost));

	rom_addr_jog <= STD_LOGIC_VECTOR(map_code & jog_room_code);
	rom_addr_mon <= STD_LOGIC_VECTOR(map_code & monster_room_code);

	current_pos <= rom_addr_jog;
	monster_current_pos <= rom_addr_mon;

	monster_next_room <= (rom_data_mon(6 DOWNTO 2)) WHEN monster_direction = "00" ELSE
		(rom_data_mon(13 DOWNTO 9)) WHEN monster_direction = "01" ELSE
		(rom_data_mon(20 DOWNTO 16)) WHEN monster_direction = "10" ELSE
		(rom_data_mon(27 DOWNTO 23));

	-- next_monster_count <= STD_LOGIC_VECTOR(unsigned(monster_count) + to_unsigned(1, 2));

	-- Random monster
	-- mon_count_reg : registrador_n GENERIC MAP(2, 0)
	-- PORT MAP(clock, reset, '1', next_monster_count, monster_count);

	reset_or_play <= reset_or_map OR room_cnt_cont;
	mon_mov : mon_mov_gen PORT MAP
		(clock, reset_or_play, rom_data_mon, jog_room_code, monster_room_code, monster_direction);

	-- Position registers
	reset_or_map <= reset OR map_cnt;
	room_cnt_cont <= room_cnt AND continue;
	mon_reg : registrador_n GENERIC MAP(5, 31)
	PORT MAP(clock, reset_or_map, room_cnt_cont, monster_next_room, monster_room_code);
	jog_reg : registrador_n GENERIC MAP(5, 0)
	PORT MAP(clock, reset_or_map, room_cnt_cont, jog_next_room_data(6 DOWNTO 2), jog_room_code);

	full_state(6 DOWNTO 2) <= monster_room_code;
	full_state(11 DOWNTO 7) <= jog_room_code;

	-- Map Register
	map_reg : registrador_n GENERIC MAP(2, 0)
	PORT MAP(clock, reset, map_cnt, next_map, map_code);
	next_map <= STD_LOGIC_VECTOR(unsigned(map_code) + to_unsigned(1, 2));
	full_state(1 DOWNTO 0) <= map_code;

	-- Last move register
	last_move_reg : registrador_n GENERIC MAP(3, 4) PORT MAP(clock, reset_or_map, room_cnt_cont, cur_move, s_last_move);
	cur_move <= "000" WHEN mov_dir = "0001" ELSE
		"001" WHEN mov_dir = "0010" ELSE
		"010" WHEN mov_dir = "0100" ELSE
		"011";
	full_state(14 DOWNTO 12) <= s_last_move;
	-- last_move <= s_last_move;

	-- Lost register

	lost_reg : registrador_n GENERIC MAP(
		1, 0) PORT MAP (
		clock => clock,
		reset => reset_or_map,
		load => room_cnt_cont,
		D => s_next_lost_v,
		Q => s_lost_v
	);
	s_next_lost_v(0) <= (jog_mon_nex_eq OR crossed) AND mode;
	s_lost <= s_lost_v(0);

	crossed_to_mon <= '1' WHEN jog_room_code = monster_next_room ELSE
		'0';
	crossed_to_jog <= '1' WHEN jog_next_room_data(6 DOWNTO 2) = monster_room_code ELSE
		'0';
	crossed_path <= '1' WHEN jog_next_room_data(1 DOWNTO 0) = monster_direction ELSE
		'0';

	crossed <= crossed_to_mon AND crossed_to_jog AND crossed_path AND (mov_dir(0) OR mov_dir(1) OR mov_dir(2) OR mov_dir(3));

	jog_mon_nex_eq <= '1' WHEN (STD_LOGIC_VECTOR(monster_next_room) = STD_LOGIC_VECTOR(jog_next_room_data(6 DOWNTO 2))) ELSE
		'0';

	--MAP LOGIC
	map_mem : rom_128x20 PORT MAP
		(rom_addr_jog, rom_addr_mon, rom_data_jog, rom_data_mon);

	room_cnt <= move_pulse;

	btns_or <= dir_btns(3) OR dir_btns(2) OR dir_btns(1) OR dir_btns(0);

	mov_dect : edge_detector PORT MAP(clock, reset, btns_or, move_pulse);

	gen_has_door : FOR i IN 0 TO 3 GENERATE
		has_door(i) <= '0' WHEN rom_data_jog(i * 7 + 6 DOWNTO i * 7 + 2) = STD_LOGIC_VECTOR(jog_room_code) ELSE
		'1';
		mov_dir(i) <= has_door(i) AND dir_btns(i);
	END GENERATE; -- gen_has_door
	walls <= has_door;

	jog_next_room_data <= (rom_data_jog(6 DOWNTO 0)) WHEN mov_dir = "0001" ELSE
		(rom_data_jog(13 DOWNTO 7)) WHEN mov_dir = "0010" ELSE
		(rom_data_jog(20 DOWNTO 14)) WHEN mov_dir = "0100" ELSE
		(rom_data_jog(27 DOWNTO 21)) WHEN mov_dir = "1000" ELSE
		jog_room_code & "00";
	s_won <= '1' WHEN STD_LOGIC_VECTOR(jog_room_code) = "11111" ELSE
		'0';

	won <= s_won;
	lost <= s_lost AND (NOT s_won);
	map_cnt <= s_won AND next_map_btn;

END behav; -- behav