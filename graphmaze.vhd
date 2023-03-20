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
	
	COMPONENT data_flux_mode_1 IS
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
	END COMPONENT;
	
	COMPONENT decoder_7seg IS
		 PORT (
			  data : IN  std_logic_vector(6 DOWNTO 0);
			  sseg_2 : OUT std_logic_vector(6 DOWNTO 0);
			  sseg_1 : OUT std_logic_vector(6 DOWNTO 0);
			  sseg_0 : OUT std_logic_vector(6 DOWNTO 0)
		 );
	END COMPONENT;

	signal aux_mode : std_logic := '0';
	signal aux_not_dir_btns : std_logic_vector(3 DOWNTO 0);
	
	--MODE 0
	signal aux_won_mode_0 : std_logic;
	signal aux_current_pos_mode_0 : std_logic_vector(6 DOWNTO 0);
	signal aux_walls_mode_0 : std_logic_vector(3 DOWNTO 0);
	
	--MODE 1
	signal aux_won_mode_1 : std_logic;
	signal aux_current_pos_mode_1 : std_logic_vector(6 DOWNTO 0);
	signal aux_monster_current_pos : std_logic_vector(6 DOWNTO 0);
	signal aux_walls_mode_1 : std_logic_vector(3 DOWNTO 0);
	signal aux_lost_mode_1 : std_logic;
	signal aux_sseg_4, aux_sseg_3 : std_logic_vector(6 DOWNTO 0);
	
	--MUX SIGNALS
	signal aux_won_select : std_logic;
	signal aux_current_pos_select : std_logic_vector(6 DOWNTO 0);
	signal aux_walls_select : std_logic_vector(5 DOWNTO 0);
BEGIN
	aux_not_dir_btns(3) <= NOT dir_btns(3);
	aux_not_dir_btns(2) <= NOT dir_btns(2);
	aux_not_dir_btns(1) <= NOT dir_btns(1);
	aux_not_dir_btns(0) <= NOT dir_btns(0);
	
	--SET MODE
	set_mode : process(clock)
	begin
		if rising_edge(clock) then
			if(aux_current_pos_select = "0000000") then aux_mode <= mode;
			else aux_mode <= aux_mode;
			end if;
		end if;
	end process;
	
	--MUXES
	aux_won_select <= aux_won_mode_1 when aux_mode = '1' else
							aux_won_mode_0;
	
	aux_current_pos_select <= aux_current_pos_mode_1 when aux_mode = '1' else
									  aux_current_pos_mode_0;
	
	aux_walls_select <= (aux_walls_mode_1(1), aux_walls_mode_1(1), aux_walls_mode_1(0), aux_walls_mode_1(3), aux_walls_mode_1(3), aux_walls_mode_1(2)) when aux_mode = '1' else
							  (aux_walls_mode_0(1), aux_walls_mode_0(1), aux_walls_mode_0(0), aux_walls_mode_0(3), aux_walls_mode_0(3), aux_walls_mode_0(2));
							  
	
	--FINAL SIGNALS
	won <= aux_won_select;
	walls <= aux_walls_select;
	
	lost <= aux_lost_mode_1 when aux_mode = '1' else
			  '0';
	
	sseg_4 <= aux_sseg_4 when aux_mode = '1' else
			  "1111111";
			  
	sseg_3 <= aux_sseg_3 when aux_mode = '1' else
			  "1111111";
	
	--COMPONENTS
	DF_MODE_0: data_flux port map(
		clock => clock,
		reset => reset,
		dir_btns => aux_not_dir_btns,
		next_map_btn => next_map_btn,
		won => aux_won_mode_0,
		walls => aux_walls_mode_0,
		current_pos => aux_current_pos_mode_0
	);
	
	DF_MODE_1: data_flux_mode_1 port map(
		clock => clock,
		reset => reset,
		dir_btns => aux_not_dir_btns,
		next_map_btn => next_map_btn,
		won => aux_won_mode_1,
		lost => aux_lost_mode_1,
		walls => aux_walls_mode_1,
		current_pos => aux_current_pos_mode_1,
		monster_current_pos => aux_monster_current_pos
	);
	
	DEC_PLAYER: decoder_7seg port map(
		data => aux_current_pos_select,
		sseg_2 => sseg_2,
		sseg_1 => sseg_1,
		sseg_0 => sseg_0
	);
	
	DEC_MONSTER: decoder_7seg port map(
		data => aux_monster_current_pos,
		sseg_2 => aux_sseg_4,
		sseg_1 => aux_sseg_3,
		sseg_0 => OPEN
	);
END behav;