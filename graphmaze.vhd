LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY graphmaze IS
    PORT (
        clock, reset : IN STD_LOGIC;
        dir_btns : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
        next_map_btn : IN STD_LOGIC;
        won : OUT STD_LOGIC;
        walls : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
        sseg_2 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		  sseg_1 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		  sseg_0 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)
    );
END graphmaze;

ARCHITECTURE behav OF graphmaze IS
	COMPONENT data_flux IS
		 PORT (
			  clock, reset : IN STD_LOGIC;
			  dir_btns : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
			  next_map_btn : IN STD_LOGIC;
			  won : OUT STD_LOGIC;
			  walls : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
			  current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)
		 );
	END COMPONENT;
	
	COMPONENT decoder_7seg IS
		 PORT (
			  data : IN  std_logic_vector(6 DOWNTO 0);
			  sseg_2 : OUT std_logic_vector(6 DOWNTO 0);
			  sseg_1 : OUT std_logic_vector(6 DOWNTO 0);
			  sseg_0 : OUT std_logic_vector(6 DOWNTO 0)
		 );
	END COMPONENT;
	
	signal aux_current_pos : std_logic_vector(6 DOWNTO 0);
BEGIN
	DF: data_flux port map(
		clock => clock,
		reset => reset,
		dir_btns => dir_btns,
		next_map_btn => next_map_btn,
		won => won,
		walls => walls,
		current_pos => aux_current_pos
	);
	
	DEC: decoder_7seg port map(
		data => aux_current_pos,
		sseg_2 => sseg_2,
		sseg_1 => sseg_1,
		sseg_0 => sseg_0
	);
END behav;