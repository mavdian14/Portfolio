

    static boolean isAnagram(String a, String b) {
        if(a.length() != b.length()){
            return false;
        }
        else{
            char[] charArray_A = (a.toLowerCase()).toCharArray();
            char[] charArray_B = (b.toLowerCase()).toCharArray();
        // sort the arrays in lexigraphical order
        java.util.Arrays.sort(charArray_A);
        java.util.Arrays.sort(charArray_B);
        
        // see if they're equal (should be if they contain same letters & frequencies of them)
        return java.util.Arrays.equals(charArray_A,charArray_B);
        }
    }

