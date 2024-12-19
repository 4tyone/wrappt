CascadeRAG begins by breaking down the document into smaller, manageable chunks. These chunks are then processed in several hierarchical steps to build a tree-like structure that organizes the content effectively:

1. Initial Categorization:
    The LLM is tasked with analyzing the document chunks and grouping them into small categories, each consisting of 3-6 chunks. The LLM assigns a concise, descriptive name (ideally one or a few words) and a short but precise desrciption to each category.

2. Medium-Sized Grouping:
    Next, the category names from the previous step are grouped into medium-sized collections, typically containing 20-30 categories per group. This step abstracts the information further into broader categories.

3. Top-Level Grouping:
    Finally, the medium-sized groups are consolidated into higher-level groups. The aim is to create a small number of overarching categories—ideally no more than 10—that provide a clear and comprehensive overview of the document's structure.

At the end of this process, the document is represented as a hierarchical tree, where the smallest units (document chunks) are grouped into categories, which are then grouped into progressively larger collections. This resembles the Global Product Classification system but tailored for organizing document content.

### Retrieving Information:
To extract information from the document:

1. Iterative Category Selection:
    Given a user query, the system starts at the highest level of the tree. It prompts the LLM to select the most relevant top-level category for the query.

2. Progressive Drilling:
    The selected category is expanded, and the LLM is again prompted to choose the most relevant sub-category. This process continues, drilling down through the tree, until the system reaches the level of the original document chunks.

3. Final Answer Generation:
    Once the system identifies the relevant chunks, the LLM uses them to generate a direct answer to the user's query.

This hierarchical organization ensures efficient navigation through the document and allows the system to retrieve highly relevant information quickly and accurately. The design also mirrors human reasoning by moving from broad categories to specific details, making it an intuitive approach for interacting with complex documents.


## Ideas to implement

- Dynamic processing and data augmentation. At any point new data can be added in
- The engine runs in a feedback loop and evaluations are tested each time a query is ran, based on that feedback the knowledge tree gets adjusted for higher accuracy
    - Can ask the user to clearify if something is not fully clear. User feedback (e.g., correcting wrong answers) dynamically improves the hierarchy over time.
    - based on this feedback optimizations also take place, if there are data chunks that are frequently requested they can be cached
- Ability for the retriever to go back a category and choose a different branch
- Versioning of the tree to be able to track it's progress and vizualize