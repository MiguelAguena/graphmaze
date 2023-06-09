LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE std.textio.ALL;

-- entidade do testbench
ENTITY graphmaze_tb IS
END ENTITY;

ARCHITECTURE tb OF graphmaze_tb IS
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
	CONSTANT mulClockPeriod : TIME := 40 us; -- frequencia 25kHz

	SIGNAL clock : STD_LOGIC := '1';
	SIGNAL mode : STD_LOGIC := '1';
	SIGNAL reset, next_map_btn, won, lost : STD_LOGIC := '0';
	SIGNAL dir_btns, not_dir_btns : STD_LOGIC_VECTOR(3 DOWNTO 0) := "0000";
	SIGNAL walls : STD_LOGIC_VECTOR(5 DOWNTO 0) := (OTHERS => '0');
	SIGNAL sseg_0, sseg_1, sseg_2, sseg_3, sseg_4 : STD_LOGIC_VECTOR(6 DOWNTO 0) := (OTHERS => '0');

	TYPE jogada IS (ri, up, le, do, win);
	TYPE t_val_jogada IS ARRAY(jogada) OF NATURAL;
	CONSTANT val_jogada : t_val_jogada := (ri => 3, up => 2, le => 1, do => 0, win => 0);

	TYPE t_jogadas IS ARRAY(NATURAL RANGE <>) OF jogada;
	CONSTANT jogadas : t_jogadas(0 TO 19) := (ri, do, do, le, le, le, le, do, ri, le, do, ri, up, do, le, do, ri, up, le, win);
	CONSTANT next_map_at : NATURAL := 1;

BEGIN
	clock <= (NOT clock) AND keep_simulating AFTER clockPeriod/2;
	DUT : graphmaze PORT MAP(
		clock => clock,
		reset => reset,
		mode => mode,
		dir_btns => not_dir_btns,
		next_map_btn => next_map_btn,
		won => won,
		lost => lost,
		walls => walls,
		sseg_4 => sseg_4,
		sseg_3 => sseg_3,
		sseg_2 => sseg_2,
		sseg_1 => sseg_1,
		sseg_0 => sseg_0
	);

	not_dir_btns <= NOT dir_btns;

	stimulus : PROCESS IS
	BEGIN
		keep_simulating <= '1';

		WAIT FOR mulClockPeriod;

		FOR i IN 0 TO jogadas'length - 1 LOOP
			IF jogadas(i) = win THEN
				next_map_btn <= '1';
				WAIT FOR 2 * mulClockPeriod;
				next_map_btn <= '0';
				WAIT FOR 10 * mulClockPeriod;
			ELSE
				dir_btns(val_jogada(jogadas(i))) <= '1';
				WAIT FOR 5 * mulClockPeriod;
				dir_btns(val_jogada(jogadas(i))) <= '0';
				WAIT FOR 20 * mulClockPeriod;
			END IF;
		END LOOP;

		reset <= '1';
		WAIT FOR mulClockPeriod;
		reset <= '0';
		WAIT FOR 4 * mulClockPeriod;
		keep_simulating <= '0';
		WAIT; -- fim da simulação: processo aguarda indefinidamente
	END PROCESS;
END ARCHITECTURE;