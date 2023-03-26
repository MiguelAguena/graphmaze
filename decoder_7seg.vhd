LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;
ENTITY decoder_7seg IS
	PORT (
		data : IN STD_LOGIC_VECTOR(6 DOWNTO 0);
		sseg_2 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		sseg_1 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
		sseg_0 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)
	);
END ENTITY decoder_7seg;

-- ARCHITECTURE comportamental OF decoder_7seg IS
-- 	TYPE t_digits_ref IS ARRAY (0 TO 15) OF STD_LOGIC_VECTOR(6 DOWNTO 0);
-- 	CONSTANT digits_ref : t_digits_ref := (
-- 		"1000000", -- 0
-- 		"1111001", -- 1
-- 		"0100100", -- 2
-- 		"0110000", -- 3
-- 		"0011001", -- 4
-- 		"0010010", -- 5
-- 		"0000010", -- 6
-- 		"1111000", -- 7
-- 		"0000000", -- 8
-- 		"0010000", -- 9
-- 		"0001000", -- A
-- 		"0000011", -- B
-- 		"1000110", -- C
-- 		"0100001", -- D
-- 		"0000110", -- E
-- 		"0001110" -- F
-- 	);

-- 	CONSTANT digit_off : STD_LOGIC_VECTOR(6 DOWNTO 0) := (OTHERS => '1');

-- 	SIGNAL dec, val : INTEGER;
-- BEGIN
-- 	sseg_2 <= digits_ref(to_integer(unsigned(data(6 DOWNTO 5))) + 1);

-- 	val <= to_integer(unsigned(data(4 DOWNTO 0))) + 1;
-- 	dec <= (val - (val MOD 10)) / 10;

-- 	sseg_1 <= digit_off WHEN (dec = 0) ELSE
-- 		digits_ref(dec);

-- 	sseg_0 <= digits_ref(val mod 10);

-- END ARCHITECTURE comportamental;

architecture comportamental of decoder_7seg is
	begin
	  
		sseg_2 <= "1111001" when data(6 downto 5)="00" else
					  "0100100" when data(6 downto 5)="01" else
					  "0110000" when data(6 downto 5)="10" else
					  "0011001" when data(6 downto 5)="11" else
				 "1111111";
					
		sseg_1 <= "1111001" when data(4 downto 0)="01001" else
					  "1111001" when data(4 downto 0)="01010" else
					 "1111001" when data(4 downto 0)="01011" else
					 "1111001" when data(4 downto 0)="01100" else
					 "1111001" when data(4 downto 0)="01101" else
					 "1111001" when data(4 downto 0)="01110" else
					 "1111001" when data(4 downto 0)="01111" else
					 "1111001" when data(4 downto 0)="10000" else
					 "1111001" when data(4 downto 0)="10001" else
					 "1111001" when data(4 downto 0)="10010" else
					 
					 "0100100" when data(4 downto 0)="10011" else
					   "0100100" when data(4 downto 0)="10100" else
					  "0100100" when data(4 downto 0)="10101" else
					 "0100100" when data(4 downto 0)="10110" else
					 "0100100" when data(4 downto 0)="10111" else
					 "0100100" when data(4 downto 0)="11000" else
					 "0100100" when data(4 downto 0)="11001" else
					 "0100100" when data(4 downto 0)="11010" else
					 "0100100" when data(4 downto 0)="11011" else
					 "0100100" when data(4 downto 0)="11100" else
					
					 "0110000" when data(4 downto 0)="11101" else
					 "0110000" when data(4 downto 0)="11110" else
					 "0110000" when data(4 downto 0)="11111" else
					 
					  "1111111";
					
		sseg_0 <= "1000000" when (data(4 downto 0)="01001" OR data(4 downto 0)="10011" OR data(4 downto 0)="11101") else
					 "1111001" when (data(4 downto 0)="00000" OR data(4 downto 0)="01010" OR data(4 downto 0)="10100" OR data(4 downto 0)="11110") else
					 "0100100" when (data(4 downto 0)="00001" OR data(4 downto 0)="01011" OR data(4 downto 0)="10101" OR data(4 downto 0)="11111") else
					 "0110000" when (data(4 downto 0)="00010" OR data(4 downto 0)="01100" OR data(4 downto 0)="10110") else
					 "0011001" when (data(4 downto 0)="00011" OR data(4 downto 0)="01101" OR data(4 downto 0)="10111") else
					 "0010010" when (data(4 downto 0)="00100" OR data(4 downto 0)="01110" OR data(4 downto 0)="11000") else
					 "0000010" when (data(4 downto 0)="00101" OR data(4 downto 0)="01111" OR data(4 downto 0)="11001") else
					 "1111000" when (data(4 downto 0)="00110" OR data(4 downto 0)="10000" OR data(4 downto 0)="11010") else
					 "0000000" when (data(4 downto 0)="00111" OR data(4 downto 0)="10001" OR data(4 downto 0)="11011") else
					 "0010000" when (data(4 downto 0)="01000" OR data(4 downto 0)="10010" OR data(4 downto 0)="11100") else
					 "1111111";
	
	end architecture comportamental;