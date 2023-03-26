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

ARCHITECTURE comportamental OF decoder_7seg IS
	TYPE t_digits_ref IS ARRAY (0 TO 15) OF STD_LOGIC_VECTOR(6 DOWNTO 0);
	CONSTANT digits_ref : t_digits_ref := (
		"1000000", -- 0
		"1111001", -- 1
		"0100100", -- 2
		"0110000", -- 3
		"0011001", -- 4
		"0010010", -- 5
		"0000010", -- 6
		"1111000", -- 7
		"0000000", -- 8
		"0010000", -- 9
		"0001000", -- A
		"0000011", -- B
		"1000110", -- C
		"0100001", -- D
		"0000110", -- E
		"0001110" -- F
	);

	CONSTANT digit_off : STD_LOGIC_VECTOR(6 DOWNTO 0) := (OTHERS => '1');

	SIGNAL dec, val : INTEGER;
BEGIN
	sseg_2 <= digits_ref(to_integer(unsigned(data(6 DOWNTO 5))) + 1);

	val <= to_integer(unsigned(data(4 DOWNTO 0))) + 1;
	dec <= (val - (val MOD 10)) / 10;

	sseg_1 <= digit_off WHEN (dec = 0) ELSE
		digits_ref(dec);

	sseg_0 <= digits_ref(val mod 10);

END ARCHITECTURE comportamental;