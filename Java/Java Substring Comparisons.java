

    public static String getSmallestAndLargest(String s, int k) {
        String smallest = "";
        String largest = "";
        // Complete the function
        // 'smallest' must be the lexicographically smallest substring of length 'k'
        // 'largest' must be the lexicographically largest substring of length 'k'

    int letras = s.length();
        for (int i = 0; i <= letras - k; i++) {
           
           if (i == 0) {
               smallest = s.substring(i, i+k);
               largest = s.substring(i, i+k);
           }
            if (s.substring(i, i+k).compareTo(smallest) <= 0) {
               smallest = s.substring(i, i+k);
            }
            if (s.substring(i, i+k).compareTo(largest) >= 0) {
                largest  = s.substring(i, i+k);
            }
           //System.out.print(s.substring(i, i+k) +", ");
           //System.out.print( s.substring(i+1, i+1+k));
        }

    return smallest + "\n" + largest;
}

