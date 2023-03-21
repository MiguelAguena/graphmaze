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
	 TYPE transitions IS ARRAY(0 TO 3) OF STD_LOGIC_VECTOR(4 DOWNTO 0);
    
	 COMPONENT rom_128x20 IS
        PORT (
            endereco : IN STD_LOGIC_VECTOR(6 DOWNTO 0);
            dado_saida : OUT STD_LOGIC_VECTOR(19 DOWNTO 0)
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

	 SIGNAL aux_current_pos : STD_LOGIC_VECTOR(6 DOWNTO 0) := "0000000";
	 SIGNAL aux_monster_current_pos : STD_LOGIC_VECTOR(6 DOWNTO 0) := "0011110";
    SIGNAL room_code, next_room : unsigned(4 DOWNTO 0) := (OTHERS => '0');
	 SIGNAL monster_room_code : unsigned(4 DOWNTO 0) := "11110";
	 SIGNAL monster_next_room : unsigned(4 DOWNTO 0) := (OTHERS => '0');
	 SIGNAL monster_rom_data : STD_LOGIC_VECTOR(19 DOWNTO 0) := (OTHERS => '0');
	 SIGNAL monster_rom_transitions : transitions := ((OTHERS => '0'), (OTHERS => '0'), (OTHERS => '0'), (OTHERS => '0'));
	 SIGNAL monster_count : integer range 0 to 3 := 0;
    SIGNAL map_code : unsigned(1 DOWNTO 0) := (OTHERS => '0');
	 SIGNAL rom_select : STD_LOGIC := '1';
    SIGNAL rom_addr : STD_LOGIC_VECTOR(6 DOWNTO 0);
    SIGNAL rom_data : STD_LOGIC_VECTOR(19 DOWNTO 0);
    SIGNAL room_cnt, map_cnt, btns_or, move_pulse, s_won, s_lost : STD_LOGIC;
    SIGNAL has_door, mov_dir : STD_LOGIC_VECTOR(3 DOWNTO 0);
	 SIGNAL continue : STD_LOGIC := '0';
BEGIN
	 continue <= (NOT(s_won) AND NOT(s_lost) AND NOT(rom_select));
	 
    main_pro : PROCESS (clock)
    BEGIN
        IF rising_edge(clock) THEN
				IF reset = '1' THEN 
					room_code <= (OTHERS => '0');
					map_code <= (OTHERS => '0');
					monster_room_code <= "11110";
					rom_select <= '1';
				ELSE
					IF (map_cnt = '1') THEN
						 map_code <= map_code + 1;
						 room_code <= (others => '0');
						 monster_room_code <= "11110";
						 rom_select <= '1';
					ELSIF (room_cnt = '1' AND continue = '1') THEN
						 room_code <= next_room;
						 monster_room_code <= monster_next_room;
						 rom_select <= '1';
					ELSIF rom_select = '1' THEN
						 rom_select <= '0';
					END IF;
				END IF;
        END IF;
    END PROCESS; -- main_pro

	 aux_current_pos <= STD_LOGIC_VECTOR(map_code & room_code);
	 aux_monster_current_pos <= STD_LOGIC_VECTOR(map_code & monster_room_code);
	 
	 --SELECT BETWEEN PLAYER AND MONSTER
	 rom_addr <= aux_monster_current_pos when rom_select = '1' else
					 aux_current_pos;
					 
	 current_pos <= aux_current_pos;
	 monster_current_pos <= aux_monster_current_pos;
					 
	 --MONSTER LOGIC
	 set_monster_rom_data : process(clock)
	 begin
		if rising_edge(clock) then
			if(rom_select = '1') then monster_rom_data <= rom_data;
			else monster_rom_data <= monster_rom_data;
			end if;
		end if;
	 end process;
	
	 monster_rom_transitions(3) <= monster_rom_data(19 DOWNTO 15);
	 monster_rom_transitions(2) <= monster_rom_data(14 DOWNTO 10);
	 monster_rom_transitions(1) <= monster_rom_data(9 DOWNTO 5);
	 monster_rom_transitions(0) <= monster_rom_data(4 DOWNTO 0);
	
	 choose_monster_next_room : process(clock)
	 begin
		if rising_edge(clock) then
			if (continue = '1' AND reset = '0' AND map_cnt = '0') then
				if (monster_count = 3) then monster_count <= 0;
				else
					monster_count <= monster_count + 1;
--					if(monster_rom_transitions(monster_count) = STD_LOGIC_VECTOR(monster_room_code)) then
--						if (monster_count = 3) then monster_count <= 0;
--						else monster_count <= monster_count + 1;
--						end if;
--					end if;
				end if;
			elsif(reset = '1' OR map_cnt = '1') then
				monster_count <= 0;
			else
				monster_count <= monster_count;
			end if;
		end if;
	 end process;
	
	 monster_next_room <= unsigned(monster_rom_transitions(monster_count));
	
	 --MAP LOGIC
    map_mem : rom_128x20 PORT MAP(rom_addr, rom_data);
	 
	 room_cnt <= move_pulse;

    btns_or <= dir_btns(3) or dir_btns(2) or dir_btns(1) or dir_btns(0);
--	 not_btns_or <= not btns_or;
    mov_dect : edge_detector PORT MAP(clock, reset, btns_or, move_pulse);

    gen_has_door : FOR i IN 0 TO 3 GENERATE
        has_door(i) <= '0' WHEN rom_data(i * 5 + 4 DOWNTO i * 5) = STD_LOGIC_VECTOR(room_code) ELSE
        '1';
        mov_dir(i) <= has_door(i) AND dir_btns(i);
    END GENERATE; -- gen_has_door
	 walls <= has_door;

    next_room <= unsigned(rom_data(4 DOWNTO 0)) WHEN (mov_dir = "0001" AND continue = '1') ELSE
					  unsigned(rom_data(9 DOWNTO 5)) WHEN (mov_dir = "0010" AND continue = '1') ELSE
					  unsigned(rom_data(14 DOWNTO 10)) WHEN (mov_dir = "0100" AND continue = '1') ELSE
                 unsigned(rom_data(19 DOWNTO 15)) WHEN (mov_dir = "1000" AND continue = '1') ELSE
					  room_code;

    s_won <= '1' WHEN STD_LOGIC_VECTOR(room_code) = "11111" ELSE
				 '0';
		  
    s_lost <= '1' WHEN STD_LOGIC_VECTOR(room_code) = STD_LOGIC_VECTOR(monster_room_code) ELSE
				  '0';
				  
	 won <= s_won;
	 lost <= s_lost;
	 map_cnt <= s_won and next_map_btn;
END behav; -- behav