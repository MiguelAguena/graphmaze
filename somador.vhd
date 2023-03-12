library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity full_adder is
    port(
        A, B, Ci  : in std_logic;
        Co, S     : out std_logic
    );
end entity full_adder;

architecture full_adder_1 of full_adder is
begin
    S <= ((A XOR B) XOR Ci);
    Co <= (A AND B) OR (A AND Ci) OR (B AND Ci);
end architecture full_adder_1;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity somador is
    port (
        A, B       : in  std_logic_vector(6 downto 0);
        S          : out std_logic_vector(6 downto 0);
        Ov         : out std_logic
    );
end somador;

architecture somador_1 of somador is
    component full_adder is
        port(
            A, B, Ci  : in std_logic;
            Co, S     : out std_logic
        );
    end component full_adder;

    signal carry_aux : std_logic_vector(6 downto 0);
begin
	GEN_FAS: for i in 6 downto 0 generate
		GEN_FIRST: if i = 0 generate
			FA0: full_adder port map(
				A => A(0),
				B => B(0),
				Ci => '0',
				Co => carry_aux(0),
				S => S(0)
			);
		end generate;
		
		GEN_OTHERS: if i > 0 generate
			FAI: full_adder port map(
				A => A(i),
				B => B(i),
				Ci => carry_aux(i - 1),
				Co => carry_aux(i),
				S => S(i)
			);
		end generate;
	end generate;
		
	Ov <= carry_aux(6);
end architecture;