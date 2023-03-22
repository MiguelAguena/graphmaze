LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY data_flux_mode_1 IS
	PORT (
		clock, reset : IN STD_LOGIC;
		dir_btns : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
		next_map_btn : IN STD_LOGIC;
		won : OUT STD_LOGIC;
		lost : OUT STD_LOGIC;
		walls : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
		current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		monster_current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)
	);
END data_flux_mode_1;

ARCHITECTURE behav OF data_flux_mode_1 IS

	COMPONENT rom_128x20 IS
		PORT (
			enderecoA : IN STD_LOGIC_VECTOR(6 DOWNTO 0);
			enderecoB : IN STD_LOGIC_VECTOR(6 DOWNTO 0);
			dado_saidaA : OUT STD_LOGIC_VECTOR(19 DOWNTO 0);
			dado_saidaB : OUT STD_LOGIC_VECTOR(19 DOWNTO 0)
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

	SIGNAL jog_room_code, jog_next_room : STD_LOGIC_VECTOR(4 DOWNTO 0) := (OTHERS => '0');
	SIGNAL monster_room_code : STD_LOGIC_VECTOR(4 DOWNTO 0) := "11110";
	SIGNAL monster_next_room : STD_LOGIC_VECTOR(4 DOWNTO 0) := (OTHERS => '0');
	SIGNAL monster_count, next_monster_count : STD_LOGIC_VECTOR(1 DOWNTO 0);
	SIGNAL map_code, next_map : STD_LOGIC_VECTOR(1 DOWNTO 0) := (OTHERS => '0');
	SIGNAL rom_addr_jog, rom_addr_mon : STD_LOGIC_VECTOR(6 DOWNTO 0);
	SIGNAL rom_data_jog, rom_data_mon : STD_LOGIC_VECTOR(19 DOWNTO 0);
	SIGNAL room_cnt, map_cnt, btns_or, move_pulse, s_won, s_lost : STD_LOGIC;
	SIGNAL has_door, mov_dir : STD_LOGIC_VECTOR(3 DOWNTO 0);
	SIGNAL continue, cruzou_to_mon, cruzou_to_jog, cruzou : STD_LOGIC := '0';

BEGIN
	continue <= (NOT(s_won) AND NOT(s_lost));

	rom_addr_jog <= STD_LOGIC_VECTOR(map_code & jog_room_code);
	rom_addr_mon <= STD_LOGIC_VECTOR(map_code & monster_room_code);
	current_pos <= rom_addr_jog;
	monster_current_pos <= rom_addr_mon;

	monster_next_room <= rom_data_mon((to_integer(unsigned(monster_count)) * 5 + 4) DOWNTO (to_integer(unsigned(monster_count)) * 5));
	next_map <= STD_LOGIC_VECTOR(unsigned(map_code) + to_unsigned(1, 2));
	next_monster_count <= STD_LOGIC_VECTOR(unsigned(monster_count) + to_unsigned(1, 2));

	mon_reg : registrador_n GENERIC MAP(5, 30)
	PORT MAP(clock, reset OR map_cnt, room_cnt AND continue, monster_next_room, monster_room_code);
	mon_count_reg : registrador_n GENERIC MAP(2, 0)
	PORT MAP(clock, reset, '1', next_monster_count, monster_count);
	jog_reg : registrador_n GENERIC MAP(5, 0)
	PORT MAP(clock, reset OR map_cnt, room_cnt AND continue, jog_next_room, jog_room_code);
	map_reg : registrador_n GENERIC MAP(2, 0)
	PORT MAP(clock, reset, map_cnt, next_map, map_code);
	cruzou_to_mon <='1' when jog_room_code = monster_next_room else
		'0';
	cruzou_to_jog <= '1' when jog_next_room = monster_room_code else
		'0';
	cruzou <= (room_cnt AND continue) AND cruzou_to_mon AND cruzou_to_jog;
	--MAP LOGIC
	map_mem : rom_128x20 PORT MAP
		(rom_addr_jog, rom_addr_mon, rom_data_jog, rom_data_mon);

	room_cnt <= move_pulse;

	btns_or <= dir_btns(3) OR dir_btns(2) OR dir_btns(1) OR dir_btns(0);
	--	 not_btns_or <= not btns_or;
	mov_dect : edge_detector PORT MAP(clock, reset, btns_or, move_pulse);

	gen_has_door : FOR i IN 0 TO 3 GENERATE
		has_door(i) <= '0' WHEN rom_data_jog(i * 5 + 4 DOWNTO i * 5) = STD_LOGIC_VECTOR(jog_room_code) ELSE
		'1';
		mov_dir(i) <= has_door(i) AND dir_btns(i);
	END GENERATE; -- gen_has_door
	walls <= has_door;

	jog_next_room <= (rom_data_jog(4 DOWNTO 0)) WHEN (mov_dir = "0001" AND continue = '1') ELSE
		(rom_data_jog(9 DOWNTO 5)) WHEN (mov_dir = "0010" AND continue = '1') ELSE
		(rom_data_jog(14 DOWNTO 10)) WHEN (mov_dir = "0100" AND continue = '1') ELSE
		(rom_data_jog(19 DOWNTO 15)) WHEN (mov_dir = "1000" AND continue = '1') ELSE
		jog_room_code;

	s_won <= '1' WHEN STD_LOGIC_VECTOR(jog_room_code) = "11111" ELSE
		'0';

--	s_lost <= '1' WHEN (STD_LOGIC_VECTOR(jog_room_code) = STD_LOGIC_VECTOR(monster_room_code) or cruzou = '1') ELSE
--		'0';

	s_lost <= '1' WHEN (STD_LOGIC_VECTOR(jog_room_code) = STD_LOGIC_VECTOR(monster_room_code)) ELSE
		'0';

	won <= s_won;
	lost <= s_lost;
	map_cnt <= s_won AND next_map_btn;

END behav; -- behav