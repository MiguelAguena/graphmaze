LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY data_flux IS
    PORT (
        clock, reset : IN STD_LOGIC;
        dir_btns : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
        next_map_btn : IN STD_LOGIC;
        won : OUT STD_LOGIC;
        walls : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
        current_pos : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)
    );
END data_flux;

ARCHITECTURE behav OF data_flux IS

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

    SIGNAL room_code, next_room : unsigned(4 DOWNTO 0) := (OTHERS => '0');
    SIGNAL map_code : unsigned(1 DOWNTO 0) := (OTHERS => '0');
    SIGNAL rom_addr : STD_LOGIC_VECTOR(6 DOWNTO 0);
    SIGNAL rom_data : STD_LOGIC_VECTOR(19 DOWNTO 0);
    SIGNAL room_cnt, map_cnt, btns_or, move_pulse, s_won : STD_LOGIC;
    SIGNAL has_door, mov_dir : STD_LOGIC_VECTOR(3 DOWNTO 0);
BEGIN

    main_pro : PROCESS (clock)
    BEGIN
        IF rising_edge(clock) THEN
				IF reset = '1' THEN 
					room_code <= (OTHERS => '0');
					map_code <= (OTHERS => '0');
				ELSE
					IF map_cnt = '1' THEN
						 map_code <= map_code + 1;
						 room_code <= (others => '0');
					ELSIF room_cnt = '1' THEN
						 room_code <= next_room;
					END IF;
				END IF;
        END IF;
    END PROCESS; -- main_pro

    room_cnt <= move_pulse;

    rom_addr <= STD_LOGIC_VECTOR(map_code & room_code);
	 current_pos <= rom_addr;
    map_mem : rom_128x20 PORT MAP(rom_addr, (others => '0') , rom_data, OPEN);

    btns_or <= dir_btns(3) or dir_btns(2) or dir_btns(1) or dir_btns(0);
--	 not_btns_or <= not btns_or;
    mov_dect : edge_detector PORT MAP(clock, reset, btns_or, move_pulse);

    gen_has_door : FOR i IN 0 TO 3 GENERATE
        has_door(i) <= '0' WHEN rom_data(i * 5 + 4 DOWNTO i * 5) = STD_LOGIC_VECTOR(room_code) ELSE
        '1';
        mov_dir(i) <= has_door(i) AND dir_btns(i);
    END GENERATE; -- gen_has_door
	 walls <= has_door;
    WITH mov_dir SELECT next_room <=
        unsigned(rom_data(4 DOWNTO 0)) WHEN "0001",
        unsigned(rom_data(9 DOWNTO 5)) WHEN "0010",
        unsigned(rom_data(14 DOWNTO 10)) WHEN "0100",
        unsigned(rom_data(19 DOWNTO 15)) WHEN "1000",
		  room_code when OTHERS;

    s_won <= '1' WHEN STD_LOGIC_VECTOR(room_code) = "11111" ELSE
        '0';
	 won <= s_won;
	 map_cnt <= s_won and next_map_btn;
END behav; -- behav