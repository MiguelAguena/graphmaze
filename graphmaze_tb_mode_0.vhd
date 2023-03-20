LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE std.textio.ALL;

-- entidade do testbench
ENTITY graphmaze_tb_mode_0 IS
END ENTITY;

ARCHITECTURE tb OF graphmaze_tb_mode_0 IS
	COMPONENT graphmaze IS
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
			  sseg_0 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)
		 );
	END COMPONENT;
	-- Configurações do clock
	SIGNAL keep_simulating : STD_LOGIC := '0'; -- delimita o tempo de geração do clock
	CONSTANT clockPeriod : TIME := 20 ns; -- frequencia 50MHz

	SIGNAL clock : std_logic := '1';
	SIGNAL mode : std_logic := '0';
	SIGNAL reset, next_map_btn, won : STD_LOGIC := '0';
	SIGNAL dir_btns, not_dir_btns : STD_LOGIC_VECTOR(3 DOWNTO 0) := "0000";
	SIGNAL walls : STD_LOGIC_VECTOR(5 DOWNTO 0) := (OTHERS => '0');
	SIGNAL sseg_0, sseg_1, sseg_2 : STD_LOGIC_VECTOR(6 DOWNTO 0) := (OTHERS => '0');

	TYPE t_jogadas IS ARRAY(NATURAL RANGE <>) OF NATURAL;
	CONSTANT jogadas : t_jogadas(0 to 3) := (3, 1, 0, 3);

BEGIN
	clock <= (NOT clock) AND keep_simulating AFTER clockPeriod/2;
	DUT : graphmaze PORT MAP(
		clock => clock,
		reset => reset,
		mode => mode,
		dir_btns => not_dir_btns,
		next_map_btn => next_map_btn,
		won => won,
		walls => walls,
		sseg_2 => sseg_2,
		sseg_1 => sseg_1,
		sseg_0 => sseg_0
	);

	not_dir_btns <= not dir_btns;
	
	stimulus : PROCESS IS
	BEGIN
		keep_simulating <= '1';

		WAIT FOR clockPeriod;

		FOR i IN 0 to 3 LOOP
			dir_btns(jogadas(i)) <= '1';
			WAIT FOR 5 * clockPeriod;
			dir_btns(jogadas(i)) <= '0';
			WAIT FOR 5 * clockPeriod;
		END LOOP;

		next_map_btn <= '1';
		WAIT FOR 5 * clockPeriod;
		next_map_btn <= '0';

		WAIT FOR 10 * clockPeriod;

		for i in 0 to 30 loop
			dir_btns(3) <= '1';
			WAIT FOR 5 * clockPeriod;
			dir_btns(3) <= '0';
			WAIT FOR 5 * clockPeriod;
		END LOOP;

		next_map_btn <= '1';
		WAIT FOR 5 * clockPeriod;
		next_map_btn <= '0';

		WAIT FOR 10 * clockPeriod;

		keep_simulating <= '0';

		WAIT; -- fim da simulação: processo aguarda indefinidamente
	END PROCESS;
END ARCHITECTURE;