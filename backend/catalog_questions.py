"""
Comprehensive Diagnostic Question Bank for NeuronPath.
Contains curated, rigorous, high-quality technical questions covering
Web Development, Programming, Data/AI, Software Engineering, Cloud/DevOps, Security, and Computer Science.

Quality Standards:
- All 4 options are balanced in length, granularity, and grammatical structure.
- Correct answer is not systematically the longest or most detailed option.
- Distractors are plausible, technically sophisticated, and conceptually related.
"""

CATALOG_QUESTIONS = [
    # =========================================================================
    # WEB DEVELOPMENT: HTML & CSS & RESPONSIVE DESIGN
    # =========================================================================
    {
        "skill": "HTML Fundamentals",
        "question": "Which HTML5 semantic element represents standalone content intended to be independently reusable (e.g. a blog post or news card)?",
        "options": [
            "<article>",
            "<section>",
            "<main>",
            "<aside>"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "The <article> element represents a self-contained composition intended to be independently distributable or reusable."
    },
    {
        "skill": "HTML Fundamentals",
        "question": "What is the primary accessibility and functional role of the `alt` attribute on an `<img>` element?",
        "options": [
            "Provides descriptive text for screen readers and when images fail to render",
            "Defines the visual tooltip text displayed when hovering over the image",
            "Specifies the fallback high-resolution URL for high-DPI retina screens",
            "Sets the title metadata stored when saving images to the local disk"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "The alt attribute provides essential alternative text for screen readers and displays when the image cannot be loaded."
    },
    {
        "skill": "HTML Fundamentals",
        "question": "In an HTML form, what is the fundamental transmission difference between `method=\"GET\"` and `method=\"POST\"`?",
        "options": [
            "`GET` appends form parameters to the URL query string; `POST` sends data inside the HTTP request body",
            "`GET` automatically encrypts parameters with TLS; `POST` transmits inputs in unencrypted plain text",
            "`POST` is cached by default in browser history; `GET` avoids caching to protect sensitive credentials",
            "`GET` requires multipart encoding on the server; `POST` processes data strictly through URL query parameters"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "GET encodes data into URL query parameters (cached, visible in history); POST transmits parameters inside the request payload body."
    },
    {
        "skill": "CSS Fundamentals",
        "question": "In the standard CSS Box Model, what are the four layers ordered from innermost to outermost?",
        "options": [
            "Content -> Padding -> Border -> Margin",
            "Content -> Margin -> Border -> Padding",
            "Padding -> Content -> Border -> Margin",
            "Border -> Padding -> Content -> Margin"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "The box model consists of Content (innermost), surrounded by Padding, Border, and Margin (outermost)."
    },
    {
        "skill": "CSS Fundamentals",
        "question": "What is the effect of setting `box-sizing: border-box;` on an HTML element?",
        "options": [
            "Includes padding and border within the element's defined width and height",
            "Adds an external box shadow equal to the element's border thickness",
            "Forces child container margins to collapse within the parent boundaries",
            "Restricts element dimensions strictly to the content text bounding box"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "border-box ensures that padding and border widths are absorbed within the declared width/height dimensions."
    },
    {
        "skill": "Responsive Design & CSS Layouts",
        "question": "In CSS Flexbox layout, what is the primary distinction between `justify-content` and `align-items`?",
        "options": [
            "`justify-content` distributes items along the main axis; `align-items` aligns items along the cross axis",
            "`justify-content` controls flex container wrapping; `align-items` sets individual item order indexes",
            "`justify-content` positions text within child elements; `align-items` controls outer margin spacing",
            "`justify-content` sets horizontal margins exclusively; `align-items` sets vertical padding exclusively"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "justify-content governs positioning along the main axis (e.g. horizontal in row), while align-items governs the cross axis."
    },
    {
        "skill": "Responsive Design & CSS Layouts",
        "question": "In a mobile-first responsive CSS workflow, how are viewport breakpoints typically structured?",
        "options": [
            "Using `min-width` media queries to progressively layer enhancements for larger screens",
            "Using `max-width` media queries to progressively remove desktop styles on mobile screens",
            "Using absolute pixel widths with fixed scale meta tags to lock viewport zoom levels",
            "Using user-agent detection scripts to dynamically inject distinct platform stylesheets"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Mobile-first CSS writes small-screen styles by default and uses `@media (min-width: ...)` to add styling for wider viewports."
    },

    # =========================================================================
    # JAVASCRIPT & MODERN ES6+ & DOM
    # =========================================================================
    {
        "skill": "JavaScript Fundamentals",
        "question": "In JavaScript, what is the difference between strict equality `===` and loose equality `==`?",
        "options": [
            "`===` compares value and type without coercion; `==` performs implicit type conversion before comparing",
            "`===` compares heap memory pointers; `==` compares primitive values stored directly on the stack",
            "`===` is restricted strictly to numeric comparisons; `==` supports string and boolean comparisons",
            "`===` evaluates true only for identical object references; `==` performs deep recursive object equality"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "Strict equality (===) checks value and type without coercion, whereas loose equality (==) coerces types before checking."
    },
    {
        "skill": "JavaScript Fundamentals",
        "question": "What is a Closure in JavaScript?",
        "options": [
            "A function retaining access to variables in its outer lexical scope after the outer function finishes",
            "A recursive function that terminates immediately when reaching its designated base case condition",
            "An object method that restricts property mutation by freezing its prototype chain during execution",
            "A browser garbage collection routine that clears unreferenced variables from memory heaps"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "A closure is created when an inner function maintains lexical scope access to variables from its outer enclosing function."
    },
    {
        "skill": "Modern ES6+ & Async JS",
        "question": "What is the settlement behavior of `Promise.all([p1, p2, p3])` when any single promise rejects?",
        "options": [
            "Immediately rejects with the reason of the first rejected promise, ignoring pending promises",
            "Waits for all remaining promises to finish and returns a collection containing null values",
            "Automatically retries the rejected promise up to three times before failing the entire batch",
            "Converts the rejection into an empty array item and resolves with all remaining successful values"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Promise.all employs fail-fast behavior: if any promise rejects, the entire returned promise rejects immediately."
    },
    {
        "skill": "Modern ES6+ & Async JS",
        "question": "How does the `async / await` syntax execute asynchronous operations in JavaScript?",
        "options": [
            "Pauses async function execution until a Promise settles without blocking the main event loop",
            "Spawns an isolated background OS thread to execute the awaited operation in parallel",
            "Blocks all browser UI rendering threads synchronously until the network response finishes",
            "Converts asynchronous callbacks directly into synchronous XMLHttpRequest operations"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "async/await pauses local function execution without blocking the browser event loop thread, resolving as microtasks."
    },
    {
        "skill": "DOM & Browser APIs",
        "question": "In DOM event propagation, what is the directional difference between Event Capturing and Event Bubbling?",
        "options": [
            "Capturing travels downward from window to target; Bubbling propagates upward from target to window",
            "Capturing handles keyboard events exclusively; Bubbling handles mouse and pointer clicks exclusively",
            "Capturing terminates event dispatching immediately; Bubbling clones the event across child elements",
            "Capturing runs asynchronously on worker threads; Bubbling executes synchronously on the UI thread"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Event dispatch begins with the capture phase (window down to target), followed by the bubbling phase (target back up to window)."
    },

    # =========================================================================
    # REACT & FRONTEND ARCHITECTURE
    # =========================================================================
    {
        "skill": "React Fundamentals",
        "question": "Why does React require a unique `key` prop when rendering dynamic lists of elements?",
        "options": [
            "Helps React identify which items have changed, been added, or been removed during reconciliation",
            "Enables automatic alphabetical sorting of list elements before rendering to the DOM tree",
            "Prevents CSS style inheritance conflicts between sibling components rendered in the same container",
            "Allocates dedicated persistent memory blocks in the browser engine for each rendered list node"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "Keys give list elements stable identities, allowing React's reconciliation diffing algorithm to update only modified items."
    },
    {
        "skill": "React State & Hooks",
        "question": "In React components, why must state updates be treated as immutable rather than mutating existing state objects?",
        "options": [
            "React relies on reference equality checks (Object.is) to detect state changes and trigger re-renders",
            "Direct mutations trigger browser security sandbox violations that abort execution in production",
            "JavaScript throws a runtime fatal TypeError when modifying properties on React state objects",
            "Mutating state objects in place causes duplicate component instances to mount in the virtual tree"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "React compares old and new state references. Mutating existing objects in place keeps the same memory pointer, causing React to skip re-rendering."
    },
    {
        "skill": "React State & Hooks",
        "question": "What is the primary function of the cleanup callback returned inside a `useEffect` hook?",
        "options": [
            "Cleans up side effects (e.g. timers, subscriptions, event listeners) before unmounting or re-running",
            "Resets all component state variables to their initial default values before the next render phase",
            "Purges cached HTTP network responses stored by the browser to reduce client-side memory usage",
            "Forces immediate garbage collection of unreferenced JavaScript objects in the browser engine"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "The cleanup function tears down subscriptions, timers, or listeners before the effect re-runs or when the component unmounts."
    },

    # =========================================================================
    # BACKEND & REST APIS & DATABASES & SECURITY
    # =========================================================================
    {
        "skill": "Backend Development",
        "question": "In an Express.js web application, what is the role of the `next()` function in middleware handlers?",
        "options": [
            "Passes execution control to the next middleware function registered in the processing stack",
            "Terminates the current client HTTP connection and sends a default status code to the browser",
            "Restarts the Node.js event loop thread to process pending asynchronous I/O operations",
            "Commits active database transactions and flushes the server response buffer to disk"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "Calling next() tells Express to invoke the next matching middleware function in the request pipeline."
    },
    {
        "skill": "RESTful API Design",
        "question": "According to REST architectural standards, which HTTP methods are defined as Idempotent?",
        "options": [
            "GET, PUT, DELETE, and HEAD",
            "POST and PATCH methods only",
            "POST, PUT, and DELETE methods",
            "GET and POST methods exclusively"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "An idempotent method (GET, PUT, DELETE, HEAD) produces the same resource state on the server regardless of whether it is called once or multiple times."
    },
    {
        "skill": "Databases & SQL",
        "question": "What core guarantees do ACID properties provide in relational database transaction management?",
        "options": [
            "Atomicity (all or nothing), Consistency (valid state), Isolation (concurrency), and Durability (persistence)",
            "Asynchronous processing, Cluster replication, Index compression, and Dynamic schema migrations",
            "Automated failover, Continuous indexing, Integrated caching, and Distributed partition balancing",
            "Access authorization, Cipher encryption, Integrity validation, and Denial-of-service protection"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "ACID ensures that database transactions are processed reliably: Atomicity, Consistency, Isolation, and Durability."
    },
    {
        "skill": "Authentication & Web Security",
        "question": "In JSON Web Token (JWT) authentication, what are the three dot-separated components of a token?",
        "options": [
            "Header (algorithm metadata), Payload (claims/data), and Signature (verification hash)",
            "Client ID (identifier), User Secret (hash), and Expiration (timestamp)",
            "Public Key (certificate), Private Key (signer), and Authority (issuer)",
            "Domain (origin), Session ID (token), and Cookie Flags (security metadata)"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "A JWT is composed of Header, Payload, and Signature, each encoded in Base64Url."
    },
    {
        "skill": "Authentication & Web Security",
        "question": "What security risk does Cross-Origin Resource Sharing (CORS) header configuration mitigate in browsers?",
        "options": [
            "Restricts unauthorized third-party websites from reading sensitive API data via client requests",
            "Prevents denial-of-service attacks by throttling high-frequency TCP connections on servers",
            "Stops SQL injection attacks by sanitizing incoming request parameter strings on databases",
            "Blocks cross-site scripting by disabling inline JavaScript execution in HTML templates"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "CORS allows API servers to declare which frontend origins are permitted to access their responses from the browser."
    },
    {
        "skill": "Test Automation & QA",
        "question": "In automated unit testing, what is the primary purpose of using a Test Mock or Stub?",
        "options": [
            "Simulates external dependencies (e.g. databases, APIs) to test code in predictable isolation",
            "Measures runtime CPU and memory performance benchmarks under simulated production traffic",
            "Generates visual interface wireframe mockups automatically from component code structures",
            "Replaces the compiler during test runs to skip syntax and type validation routines"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "Mocks and stubs isolate the code under test by replacing unpredictable external systems with controlled fake responses."
    },
    {
        "skill": "Full-Stack Project Architecture",
        "question": "Why is Database Connection Pooling used in backend web server architectures?",
        "options": [
            "Reuses pre-established database connections to eliminate the latency of opening TCP connections per request",
            "Replicates relational database tables automatically across multiple server memory caches for faster queries",
            "Converts incoming SQL queries into client-side JavaScript objects to offload compute from database engines",
            "Encrypts database communication channels dynamically without requiring SSL/TLS certificate configurations"
        ],
        "correct": 0,
        "difficulty": "advanced",
        "explanation": "Connection pools maintain open database connections for reuse, avoiding the high overhead of establishing new TCP sockets on every request."
    },

    # =========================================================================
    # DOCKER & CONTAINERIZATION & DEVOPS
    # =========================================================================
    {
        "skill": "Docker Basics",
        "question": "What is the primary architectural difference between a Docker Image and a Docker Container?",
        "options": [
            "An image is an immutable build blueprint; a container is an active, runnable instance of an image",
            "An image runs directly on the bare-metal kernel; a container requires a dedicated hypervisor layer",
            "Images store mutable runtime execution state; containers store static build-time layer instructions",
            "An image is compiled machine assembly code; a container is interpreted high-level shell script"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "An image is an immutable template containing instructions, and a container is an isolated running instance of that template."
    },
    {
        "skill": "Docker Basics",
        "question": "In a Dockerfile, what is the operational difference between the `RUN` and `CMD` instructions?",
        "options": [
            "`RUN` executes commands during image build to create layers; `CMD` specifies default container startup commands",
            "`RUN` sets container environment variables; `CMD` compiles application source code files during boot",
            "`RUN` is used strictly in production containers; `CMD` is executed only in local development containers",
            "`CMD` commits filesystem layer changes at build time; `RUN` executes on container runtime boot"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "RUN builds layers by executing commands during build time; CMD defines the default command executed when a container starts."
    },
    {
        "skill": "Docker Basics",
        "question": "Why are Docker Multi-Stage builds recommended for production application images?",
        "options": [
            "They separate build dependencies from runtime binaries, significantly shrinking image sizes and attack surface",
            "They enable multiple application containers to share a single host network port simultaneously",
            "They eliminate the requirement for remote container registry storage like Docker Hub or ECR",
            "They automatically convert x86 container architectures into ARM instructions at runtime"
        ],
        "correct": 0,
        "difficulty": "advanced",
        "explanation": "Multi-stage builds leave heavy compilers and tools behind in build stages, copying only compiled outputs into lean production images."
    },
    {
        "skill": "Container Networking & Storage",
        "question": "Which Docker storage mechanism persists data outside container lifecycles on host filesystems managed by Docker?",
        "options": [
            "Docker Volumes",
            "Anonymous tmpfs mounts",
            "Container writable layers",
            "UnionFS overlay memory"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Docker Volumes are managed by Docker on the host filesystem and persist independently of container lifecycles."
    },
    {
        "skill": "CI/CD Pipelines",
        "question": "In continuous integration and delivery pipelines, what is the primary purpose of an Artifact Repository?",
        "options": [
            "Stores and versions immutable build outputs (e.g. packages, images) for deterministic environment deployment",
            "Replaces source version control systems by managing Git commit histories across distributed developer teams",
            "Dynamically alters application syntax at runtime to match target cloud operating system specifications",
            "Manages public DNS routing configurations between staging and production web server clusters"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Artifact repositories preserve validated, versioned build artifacts so the exact same binary is deployed to staging and production."
    },
    {
        "skill": "Kubernetes Orchestration",
        "question": "What is the smallest deployable computing unit in Kubernetes architecture?",
        "options": [
            "Pod",
            "Node",
            "Cluster",
            "ReplicaSet"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "A Pod is the smallest deployable unit in Kubernetes, wrapping one or more containers sharing network and storage."
    },
    {
        "skill": "Linux Command Line",
        "question": "What permission set does the command `chmod 755 script.sh` apply to a file in a Linux system?",
        "options": [
            "Read, Write, Execute for Owner; Read and Execute for Group and Others",
            "Full Read, Write, and Execute permissions for all users on the host system",
            "Read and Write for Owner; restricted to Execute only for Group and Others",
            "Write and Execute for Owner; restricted strictly to Read for Others"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "7 (rwx) for owner, 5 (r-x) for group, 5 (r-x) for others. Read=4, Write=2, Execute=1."
    },
    {
        "skill": "Git & Version Control",
        "question": "What is the primary history difference between `git merge` and `git rebase`?",
        "options": [
            "`git merge` preserves full history with a merge commit; `git rebase` creates a linear history by re-applying commits",
            "`git rebase` deletes previous branch commits; `git merge` creates redundant copies of all repository files",
            "`git merge` works only on local branches; `git rebase` executes strictly against remote origin repositories",
            "`git merge` is destructive to commit history; `git rebase` maintains all original branching timestamps"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Rebase replays commits on top of another branch tip creating linear history, while merge creates a dedicated commit tying branches together."
    },

    # =========================================================================
    # DATA ANALYST & SQL & STATISTICS
    # =========================================================================
    {
        "skill": "SQL Fundamentals",
        "question": "What is the standard execution order of clauses in an SQL SELECT statement?",
        "options": [
            "FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT",
            "SELECT -> FROM -> WHERE -> GROUP BY -> HAVING -> ORDER BY -> LIMIT",
            "FROM -> SELECT -> WHERE -> ORDER BY -> GROUP BY -> HAVING -> LIMIT",
            "WHERE -> FROM -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "SQL evaluates FROM first, then WHERE filtering, GROUP BY aggregation, HAVING filters, SELECT projection, ORDER BY, and LIMIT."
    },
    {
        "skill": "SQL Advanced",
        "question": "How do `RANK()` and `DENSE_RANK()` window functions handle ranking after tied values?",
        "options": [
            "`RANK()` leaves gaps in rank numbering after ties (1, 2, 2, 4); `DENSE_RANK()` assigns consecutive numbers (1, 2, 2, 3)",
            "`DENSE_RANK()` sorts values in descending order; `RANK()` sorts values exclusively in ascending order",
            "`RANK()` operates over partitioned data subsets; `DENSE_RANK()` operates only across whole database tables",
            "`DENSE_RANK()` outputs floating point percentiles; `RANK()` outputs integer rank numbers exclusively"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "RANK skips numbers after ties to account for duplicate counts, whereas DENSE_RANK assigns unbroken consecutive integers."
    },
    {
        "skill": "Data Cleaning",
        "question": "When handling missing numeric values in heavily skewed data, why is median imputation preferred over mean imputation?",
        "options": [
            "The median is robust against extreme outlier values, whereas the mean is distorted by extreme values",
            "The median transforms skewed data distributions into standard normal Gaussian curves automatically",
            "The arithmetic mean cannot be calculated accurately on floating point column data types in SQL",
            "The median calculation consumes significantly less memory and CPU processing time during dataset loads"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "The median represents the 50th percentile and is resistant to outliers that pull the arithmetic mean toward skewed tails."
    },
    {
        "skill": "Descriptive Statistics",
        "question": "Which chart type is most effective for visualizing the median, quartiles, and outliers of numerical data across categories?",
        "options": [
            "Box Plot (Box-and-Whisker Plot)",
            "Stacked Area Chart",
            "Donut Chart",
            "Radial Radar Chart"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "Box plots display median, IQR boundaries (25th and 75th percentiles), whiskers, and outliers across groups."
    },
    {
        "skill": "Inferential Statistics",
        "question": "In statistical hypothesis testing, what conclusion is drawn when a p-value of 0.02 is obtained at an alpha level of 0.05?",
        "options": [
            "Reject the null hypothesis because the observed effect is statistically significant at the 5% level",
            "Accept the null hypothesis because the calculated p-value indicates a 98% probability of true neutrality",
            "Retain the null hypothesis because experimental results must match alpha exactly to achieve significance",
            "Discard the experimental test dataset as inconclusive due to excessive variance in sample observations"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "When p-value < alpha (0.02 < 0.05), we reject the null hypothesis in favor of the alternative hypothesis."
    },

    # =========================================================================
    # JAVA & OBJECT ORIENTED PROGRAMMING
    # =========================================================================
    {
        "skill": "Java Fundamentals",
        "question": "In Java, what is the core functional difference between String, StringBuilder, and StringBuffer?",
        "options": [
            "String is immutable; StringBuilder is mutable and non-synchronized; StringBuffer is mutable and thread-safe",
            "String is stored on thread stacks; StringBuilder and StringBuffer are allocated in disk storage",
            "StringBuilder stores numeric primitive data; StringBuffer stores character string sequences exclusively",
            "String cannot be converted to character arrays; StringBuilder and StringBuffer support character conversion"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "String is immutable; StringBuilder is mutable without synchronization overhead; StringBuffer is synchronized for multi-threaded safety."
    },
    {
        "skill": "Java OOP & Collections",
        "question": "What are the four foundational pillars of Object-Oriented Programming (OOP)?",
        "options": [
            "Encapsulation, Abstraction, Inheritance, and Polymorphism",
            "Compilation, Interpretation, Garbage Collection, and JIT Optimization",
            "Concurrency, Synchronization, Deadlock Prevention, and Thread Safety",
            "Variables, Functions, Conditional Statements, and Loop Iteration"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "The four OOP pillars are Encapsulation (data hiding), Abstraction (hiding implementation), Inheritance (code reuse), and Polymorphism."
    },
    {
        "skill": "Java OOP & Collections",
        "question": "In Java Collections Framework, what is the average time complexity for `get(key)` and `put(key, value)` in a `HashMap`?",
        "options": [
            "O(1) constant time complexity",
            "O(log N) logarithmic time complexity",
            "O(N) linear time complexity",
            "O(N^2) quadratic time complexity"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "HashMap uses hash buckets to achieve O(1) constant average lookup and insertion time complexity."
    },
    {
        "skill": "Spring Boot & Enterprise Java",
        "question": "What is the primary purpose of Dependency Injection (DI) in the Spring Boot framework?",
        "options": [
            "Supplies component dependencies at runtime through an IoC container to decouple creation from execution",
            "Injects CSS stylesheets and client scripts into HTML templates before sending responses to web browsers",
            "Compiles Java source code directly into native OS machine assembly during application startup",
            "Validates SQL schema migrations automatically against production databases during deployment cycles"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Dependency Injection decouples object creation from business logic, making components modular, configurable, and easily testable."
    },

    # =========================================================================
    # MACHINE LEARNING & ARTIFICIAL INTELLIGENCE
    # =========================================================================
    {
        "skill": "ML Fundamentals",
        "question": "What is the Bias-Variance tradeoff in supervised machine learning models?",
        "options": [
            "High bias causes underfitting from overly simple assumptions; high variance causes overfitting from noise sensitivity",
            "High bias increases GPU memory consumption; high variance increases training computation time exponentially",
            "Bias is measured strictly in classification tasks; variance is measured strictly in regression tasks",
            "Bias evaluates dataset sample counts; variance evaluates missing feature value percentages in input data"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Bias is error from erroneous model assumptions (underfitting); variance is error from sensitivity to training noise (overfitting)."
    },
    {
        "skill": "Linear & Logistic Regression",
        "question": "In binary logistic regression, what mathematical function maps linear inputs to a bounded (0, 1) probability range?",
        "options": [
            "Sigmoid (Logistic) function: 1 / (1 + e^(-z))",
            "ReLU (Rectified Linear Unit) function: max(0, z)",
            "Linear Identity function: f(z) = z",
            "Step activation function: 1 if z >= 0 else 0"
        ],
        "correct": 0,
        "difficulty": "easy",
        "explanation": "The Sigmoid activation function maps unbounded real numbers into a smooth (0, 1) probability curve."
    },
    {
        "skill": "Model Evaluation & Tuning",
        "question": "When evaluating an imbalanced classification dataset (e.g. 99% negative, 1% fraud), why is Accuracy misleading?",
        "options": [
            "A naive model predicting 'negative' for all samples achieves 99% accuracy while detecting zero fraud cases",
            "Accuracy calculations are restricted mathematically to balanced multi-class datasets with equal distributions",
            "Accuracy values cannot exceed 50% on datasets with severe target class distribution skew",
            "Accuracy scores require k-fold cross validation folds to have perfectly matched sample counts"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "Accuracy is dominated by majority class predictions; metrics like Precision, Recall, and PR-AUC reveal true minority class detection performance."
    },
    {
        "skill": "Deep Learning with PyTorch",
        "question": "In PyTorch model training loops, what is the role of invoking `loss.backward()`?",
        "options": [
            "Computes gradients of the loss with respect to model parameters using reverse-mode automatic differentiation",
            "Updates the neural network weight values using the configured optimizer learning rate parameter",
            "Clears stored gradient buffers in memory to prevent accumulation from previous training iterations",
            "Serializes the active model architecture and learned weight tensors to local filesystem checkpoints"
        ],
        "correct": 0,
        "difficulty": "intermediate",
        "explanation": "loss.backward() computes gradients of the loss function with respect to all trainable tensors using autograd."
    }
]
