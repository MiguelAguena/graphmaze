library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity left_shifter_to_5 is
   port (       
		i : in  std_logic_vector(6 downto 0);
      o : out std_logic_vector(6 downto 0)
   );
end entity left_shifter_to_5;

architecture left_shifter_to_5_arch of left_shifter_to_5 is
begin
	GEN: for a in 6 downto 0 generate
		GEN_MAIN: if a >= 5 generate
			o(a) <= i(a - 5);
		end generate;
		GEN_LAST: if a < 5 generate
			o(a) <= '0';
		end generate;
	end generate;
end architecture;