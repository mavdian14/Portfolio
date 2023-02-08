import java.util.*;
import java.util.List;
import java.util.Scanner;
import java.util.regex.Pattern;
class Solution{
	
	public static void main(String []args)
	{
		Scanner sc = new Scanner(System.in);
		
		while (sc.hasNext()) {
			String input = sc.next();

        int length1 = input.length();        
        int length2 = -1;    

        while (length2 < length1) {
            length1 = input.length();
            input = 
                Pattern.compile("[(][)]|[{][}]|[\\[][\\]]")
                .matcher(input)
                .replaceAll("");
            length2 = input.length();
        }

        System.out.println(input.length() == 0);
        }
    }
}



