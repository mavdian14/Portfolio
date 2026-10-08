import java.util.Scanner;
import java.util.regex.*;

public class Solution
{
	public static void main(String[] args){
		Scanner in = new Scanner(System.in);
		int testCases = Integer.parseInt(in.nextLine());
        String VALID = "Valid";
        String INVALID = "Invalid";
        Pattern pat;
		while(testCases>0){
			String pattern = in.nextLine().trim();
            // Returns true if, and only if, length() is 0
          	if(!pattern.isEmpty()){
                  try{
                      //Compiles the given regular expression into a pattern.
                      pat = Pattern.compile(pattern);
                      System.out.println(VALID);
                  } catch (PatternSyntaxException e){
                      System.out.println(INVALID);
                  }
                  }
                  testCases--;
              }
		}
	}



