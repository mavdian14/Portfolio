

//Complete the classes below
class Flower {
    public String whatsYourName(){
        // Returns the simple name of the underlying class as given in the source code. Returns an empty string if the underlying class is anonymous.
        return this.getClass().getSimpleName();
    }
}

class Jasmine extends Flower {
}

class Lily extends Flower {
}

class Region {
    public Flower yourNationalFlower(){
        return new Flower();
    }
}

class WestBengal extends Region{
    
    @Override
    public Flower yourNationalFlower(){
        return new Jasmine();
    }
}

class AndhraPradesh extends Region{
    
    @Override
    public Flower yourNationalFlower(){
        return new Lily();
    }
}

