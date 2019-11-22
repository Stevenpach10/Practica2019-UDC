class Capacitive
{
    // Class Member Variables
    // These are initialized at startup
    int cap; // the number of the capacitive sensor pin

    int capState; // capState used to set the capacitive sensor

    // Constructor - creates a Capacitivo
    // and initializes the member variables and state
  public:
    Capacitive(int pin)
    {
        cap = pin;
        pinMode(cap, INPUT);
        capState = LOW;
    }

    byte getState()
    {
        // check to see if the state of the capacitive sensor has changed
        capState = digitalRead(cap);

        if (capState == HIGH){
            return 0x01;
        } else {
            return 0x00;
        }
    }
};
