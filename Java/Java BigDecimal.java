
        // Use a comparator with generics to receive String parameters in compare method
        
        Arrays.sort(s,0,n,new Comparator<String>() {
            @Override
            public int compare(String s1,String s2) {
                return new BigDecimal(s2).compareTo(new BigDecimal(s1));
            }
        });

