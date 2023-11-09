# data_integration_and_large_scale_analysis
Project from course Data Integration and Large Scale Analysis on TU Graz

Address:
    Identify different Segments (separated by ",")
        If less than 3 reject
        first from right: Only 2 letters (&ZipCode in Yelp) -> State
        next one: check with cities in State
        iterate over next segments
            if includes number: Address, check with addresses in City
            if not: skip, unless new york: handle special case 
        end: if no address found reject

    State
    Phone
    City

    100 address, queens, NYC, NY
    100 address, queens, NY
    100 address, NYC, NY
    100 address, NY, NY

    New York special rules for State/Regions
        also check city in state api

    remove Ratings & No of Reviews

    Typos for Address/City:
        - Exact Match
        - Check again with Similarity Measure (Levenshtein or Token, etc...)


    Questions:
        Symbols, encoding, transform and features
        only accuracy value or more

    A1 B1 
    A2 B2
    A3 B3
    A4 B4

    16x LEV
    16x - 4x for each correct address LEV