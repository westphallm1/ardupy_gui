#include<Arduino.h>
#include"SerialInts.h"
#include"QueueList.h"
/* Constructor
 */
SerialInts::SerialInts(char sep,int size, unsigned long wait){
  _sep = sep;
  _wait = wait;
  _values = QueueList<int>();
  _curr_byte = 0;
  _curr_int = 0;
  _in_byte = 0;
  _got_byte = false;
  _char_code = '\0';
};

/* Call this every cycle of loop
* Reads a character in from Serial if one exists
*/
void SerialInts::scan(){
  if(Serial.available()){
    _got_byte = true;
    _in_byte = Serial.read();
    parse_byte();
  } else if((!_got_byte) && (_wait) && millis() > _wait){
    _wait = 0;
    //"read in" some example values if no input is detected after a certain time
    Serial.print("Input timed out. Starting demo.");
    demo();
  }
};

void SerialInts::parse_byte(){
  if((_in_byte==_sep)||_in_byte=='.'||_in_byte=='-' ||
                ((_in_byte >= '0')&&(_in_byte <='9'))){
    _bytes[_curr_byte++] = _in_byte;
    if(!_in_byte){
      //FIXME this doesn't work if _sep .NE. '\0'
      if(_curr_byte>1)_values.push(atoi(_bytes));
      _curr_byte = 0;

    }
  } else {
    handle_output_request(_in_byte);
  }
};

void SerialInts::handle_output_request(char key){
  //'n' is reserved for a no-op
  if(key == 'n') return;
  else _char_code = key;
}

char SerialInts::getCharCode(){
  return _char_code;
}

int SerialInts::length(){
  return _values.count();
}

int SerialInts::getInt(){
  return _values.pop();
}
void SerialInts::clear(){
  _curr_int = 0;
}
void SerialInts::demo(){
  int example_length = 8;
  int example_values[] = {800,0, 0,0, 800,0, 0,0};
  int i;
  for(i = 0; i < example_length; _values.push(example_values[i++]));
}
SerialInts::~SerialInts(){

};
