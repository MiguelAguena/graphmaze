int selPin0 = 8;
int selPin1 = 9;
int selPin2 = 10;
int selPin3 = 11;
int selPin4 = 12;

// int readyPin = 6;
int dataPin = 4;

void setup() {

  pinMode(selPin0, OUTPUT);
  pinMode(selPin1, OUTPUT);
  pinMode(selPin2, OUTPUT);
  pinMode(selPin3, OUTPUT);
  pinMode(selPin4, OUTPUT);

  // pinMode(readyPin, INPUT);
  pinMode(dataPin, INPUT);

  Serial.begin(9600);
}

int get_bin_digit(int val, int pos) {
  if (val == 0)
    return 0;
  int digit = val % 2;
  int nex_val = (val - digit) / 2;
  if (pos == 0)
    return digit;
  else
    return get_bin_digit(nex_val, pos - 1);
}

int read_word(int wor_len, int addr_desloc) {
  int val = 0;
  // for (int i = 0; i < wor_len; i++) {
  int i = 0;
  while (i < wor_len) {
    digitalWrite(selPin0, get_bin_digit(i + addr_desloc, 0));
    digitalWrite(selPin1, get_bin_digit(i + addr_desloc, 1));
    digitalWrite(selPin2, get_bin_digit(i + addr_desloc, 2));
    digitalWrite(selPin3, get_bin_digit(i + addr_desloc, 3));
    digitalWrite(selPin4, get_bin_digit(i + addr_desloc, 4));
    // delay(1);
    i++;
    val += digitalRead(dataPin) ? int(ceil(pow(2, i - 1))) : 0;
  }
  return val;
}

// int last_val0 = -1;
// int last_val1 = -1;
// int last_val2 = -1;
// int last_val3 = -1;

int last_map = -1;
int last_cur_pos = -1;
int last_mon_pos = -1;
int last_last_move = -1;
int last_mode = -1;
int last_lost = -1;

void loop() {
  int map = read_word(2, 0);
  int mon_pos = read_word(5, 2);
  int cur_pos = read_word(5, 7);
  int last_move = read_word(3, 12);
  int mode = read_word(1, 15);
  int lost = read_word(1, 16);

  int map_c = read_word(2, 0);
  int mon_pos_c = read_word(5, 2);
  int cur_pos_c = read_word(5, 7);
  int last_move_c = read_word(3, 12);
  int mode_c = read_word(1, 15);
  int lost_c = read_word(1, 16);

  // int val0 = read_word(4, 0);
  // int val1 = read_word(4, 4);
  // int val2 = read_word(4, 8);
  // int val3 = read_word(4, 12);

  // int val0_c = read_word(4, 0);
  // int val1_c = read_word(4, 4);
  // int val2_c = read_word(4, 8);
  // int val3_c = read_word(4, 12);

  if ((map == map_c && cur_pos == cur_pos_c && mon_pos == mon_pos_c && last_move == last_move_c && mode == mode_c && lost == lost_c) && 
      (map != last_map || cur_pos != last_cur_pos || mon_pos != last_mon_pos || last_move != last_last_move || mode != last_mode || lost != last_lost))
  {
    Serial.print("{\"mode\": ");
    Serial.print(mode);
    Serial.print("    ,\"move\": ");
    Serial.print(last_move);
    Serial.print("    ,\"jogador\": ");
    Serial.print(cur_pos);
    Serial.print("    ,\"monstro\": ");
    Serial.print(mon_pos);
    Serial.print("    ,\"mapa\": ");
    Serial.print(map);
    Serial.print("    ,\"perdeu\": ");
    Serial.print(lost);
    Serial.print("}");
    Serial.println();
    last_map = map;
    last_cur_pos = cur_pos;
    last_mon_pos = mon_pos;
    last_last_move = last_move;
    last_mode = mode;
    last_lost = lost;
  }
  // else {
    // Serial.println("{}");
  // }
}
