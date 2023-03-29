LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

--MODE 0: NORMAL MODE
--MODE 1: MONSTER MODE

--SSEG_4, SSEG_3: MONSTER POSITION
--SSEG_2, SSEG_1: PLAYER POSITION
--SSEG_0: MAP
ENTITY graphmaze IS
	PORT (
		clock, reset : IN STD_LOGIC;
		mode : IN STD_LOGIC;
		dir_btns : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
		next_map_btn : IN STD_LOGIC;
		won : OUT STD_LOGIC;
		lost : OUT STD_LOGIC;
		walls : OUT STD_LOGIC_VECTOR(5 DOWNTO 0);
		sseg_4 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		sseg_3 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		sseg_2 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		sseg_1 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		sseg_0 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		full_state_addr : in std_logic_vector(4 downto 0);
		full_state_bit : OUT STD_LOGIC
	);
END graphmaze;

ARCHITECTURE behav OF graphmaze IS
	COMPONENT data_flux IS
		PORT (
			clock, reset, mode : IN STD_LOGIC;
			dir_btns : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
			next_map_btn : IN STD_LOGIC;
			won : OUT STD_LOGIC;
			lost : OUT STD_LOGIC;
			walls : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
			current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
			monster_current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
			full_state : OUT STD_LOGIC_VECTOR(14 DOWNTO 0)
		);
	END COMPONENT;

	COMPONENT decoder_7seg IS
		PORT (
			data : IN STD_LOGIC_VECTOR(6 DOWNTO 0);
			sseg_2 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
			sseg_1 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
			sseg_0 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)
		);
	END COMPONENT;

	COMPONENT clock_mul IS
		GENERIC (
			half_factor : NATURAL
		);
		PORT (
			clock : IN STD_LOGIC;
			mul_clock : OUT STD_LOGIC
		);
	END COMPONENT;

	SIGNAL mul_clock : STD_LOGIC;
	SIGNAL cur_mode : STD_LOGIC := '0';
	SIGNAL not_dir_btns : STD_LOGIC_VECTOR(3 DOWNTO 0);

	SIGNAL cur_pos, monster_cur_pos : STD_LOGIC_VECTOR(6 DOWNTO 0);
	SIGNAL s_walls : STD_LOGIC_VECTOR(3 DOWNTO 0);
	SIGNAL s_lost, s_won : STD_LOGIC;
	SIGNAL aux_sseg_4, aux_sseg_3 : STD_LOGIC_VECTOR(6 DOWNTO 0);
	SIGNAL full_state_df : STD_LOGIC_VECTOR(14 DOWNTO 0);
	SIGNAL full_state : STD_LOGIC_VECTOR(16 DOWNTO 0);

BEGIN
	clock_gen : clock_mul GENERIC MAP(1000) PORT MAP(clock, mul_clock);

	not_dir_btns <= NOT dir_btns;

	--SET MODE
	set_mode : PROCESS (mul_clock)
	BEGIN
		IF rising_edge(mul_clock) THEN
			--			IF (reset = '1') THEN
			--				cur_mode <= '0';
			IF (cur_pos = "0000000") THEN
				cur_mode <= mode;
			ELSE
				cur_mode <= cur_mode;
			END IF;
		END IF;
	END PROCESS;

	won <= s_won;
	lost <= s_lost;
	walls <= (s_walls(1), s_walls(1), s_walls(0), s_walls(3), s_walls(3), s_walls(2));

	sseg_4 <= aux_sseg_4 WHEN cur_mode = '1' ELSE
		"1111111";

	sseg_3 <= aux_sseg_3 WHEN cur_mode = '1' ELSE
		"1111111";

	DF : data_flux PORT MAP(
		clock => mul_clock,
		reset => reset,
		mode => cur_mode,
		dir_btns => not_dir_btns,
		next_map_btn => next_map_btn,
		won => s_won,
		lost => s_lost,
		walls => s_walls,
		current_pos => cur_pos,
		monster_current_pos => monster_cur_pos,
		full_state => full_state_df
	);
	
	full_state <= s_lost & cur_mode & full_state_df;
	
	full_state_bit <= full_state(to_integer(unsigned(full_state_addr)));

	DEC_PLAYER : decoder_7seg PORT MAP(
		data => cur_pos,
		sseg_2 => sseg_2,
		sseg_1 => sseg_1,
		sseg_0 => sseg_0
	);

	DEC_MONSTER : decoder_7seg PORT MAP(
		data => monster_cur_pos,
		sseg_2 => OPEN,
		sseg_1 => aux_sseg_4,
		sseg_0 => aux_sseg_3
	);
END behav;