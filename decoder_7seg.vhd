LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;


entity decoder_7seg is
    port (
        data : in  std_logic_vector(6 downto 0);
        sseg_2 : out std_logic_vector(6 downto 0);
		  sseg_1 : out std_logic_vector(6 downto 0);
		  sseg_0 : out std_logic_vector(6 downto 0)
    );
end entity decoder_7seg;

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
