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

    project structure mockup
        configparser
            file1
            file2
            outputfile1
            outputfile2
            outputfileM

        datacleaning(file1, outputfile1)
        datacleaning(file2, outputfile2)
        feature_encoding_cleaning_symbols(outputfile1) -> outputfile1
        feature_encoding_cleaning_symbols(outputfile2) -> outputfile2

        create_blocking(outputfile1) -> block1(ids)
        create_blocking(outputfile2) -> block2(ids)

        find_duplicates(block1) -> ids1
        find_duplicates(block2) -> ids2

        delete_duplicates(ids1, outputfile1) -> outputfile1
        delete_duplicates(ids2, outputfile2) -> outputfile2

        merge_blocks(blocks1, blocks2) -> blocksM
        find_duplicates(blocksM) -> idsM
        create_comparison(outputfile1, outputfile2, idsM) -> outputfileM
        evaluate(outputfileM, labeled_data) -> percentage, extra info, etc.

