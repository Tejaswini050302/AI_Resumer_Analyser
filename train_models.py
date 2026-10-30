import os
import random
import pandas as pd
import numpy as np
from src.ml_classifier import JobRoleClassifier


# Templates and skill pools per role to generate a robust, diverse dataset
ROLE_PROFILES = {
    "Machine Learning Engineer": {
        "skills": [
            "python", "pytorch", "tensorflow", "keras", "scikit-learn", "deep learning",
            "machine learning", "nlp", "computer vision", "docker", "fastapi", "mlops",
            "hugging face", "transformers", "xgboost", "onnx", "mlflow", "linux", "git"
        ],
        "buzzwords": [
            "trained neural network models for predictive inference",
            "deployed microservices using Docker and FastAPI on cloud cluster",
            "optimized transformer latency with ONNX runtime quantization",
            "designed automated MLOps pipelines using MLflow and DVC",
            "fine-tuned BERT and LLM architectures for named entity recognition",
            "implemented convolutional neural networks for real-time object classification",
            "evaluated model performance using AUC-ROC, F1-score, and perplexity metrics"
        ]
    },
    "Data Scientist": {
        "skills": [
            "python", "r", "pandas", "numpy", "scipy", "scikit-learn", "sql", "tableau",
            "power bi", "matplotlib", "seaborn", "statistical analysis", "a/b testing",
            "feature engineering", "predictive modeling", "clustering", "xgboost"
        ],
        "buzzwords": [
            "conducted exploratory data analysis and feature engineering on transactional datasets",
            "built predictive classification and regression models to forecast customer churn",
            "designed rigorous A/B experiments and formulated statistical hypothesis tests",
            "extracted actionable business insights from multi-terabyte data warehouses using SQL",
            "presented interactive analytical dashboards to executive stakeholders using Tableau",
            "performed customer segmentation using K-means clustering and dimensionality reduction"
        ]
    },
    "Full Stack Developer": {
        "skills": [
            "javascript", "typescript", "react", "node.js", "express", "mongodb", "postgresql",
            "html5", "css3", "tailwind css", "rest api", "graphql", "git", "docker", "redux"
        ],
        "buzzwords": [
            "architected full stack web applications from client interface to database persistence",
            "built responsive Single Page Applications (SPA) using React, Redux, and Tailwind CSS",
            "engineered high-throughput RESTful endpoints using Node.js and Express",
            "designed normalized relational schemas in PostgreSQL and document collections in MongoDB",
            "implemented JWT authentication, RBAC authorization, and third-party OAuth integrations",
            "configured CI/CD workflows and Dockerized applications for seamless deployments"
        ]
    },
    "Frontend Developer": {
        "skills": [
            "javascript", "typescript", "react", "next.js", "vue", "html", "html5", "css",
            "css3", "tailwind css", "sass", "bootstrap", "redux", "responsive design", "git", "figma"
        ],
        "buzzwords": [
            "translated high-fidelity Figma designs into pixel-perfect responsive web pages",
            "built modular, reusable UI components utilizing React hooks and state management",
            "optimized Core Web Vitals, asset bundling, and client-side rendering speed",
            "ensured cross-browser compatibility and strict WCAG accessibility compliance",
            "integrated backend REST and GraphQL APIs using Axios and React Query"
        ]
    },
    "Backend Developer": {
        "skills": [
            "python", "django", "fastapi", "flask", "java", "spring boot", "postgresql",
            "mysql", "redis", "rest api", "microservices", "docker", "kafka", "git", "linux"
        ],
        "buzzwords": [
            "engineered distributed microservices architecture capable of processing 10k requests/sec",
            "implemented caching layers using Redis to reduce database query latency by 45%",
            "designed RESTful APIs and asynchronous message broker consumers using Apache Kafka",
            "optimized relational database queries, table indexing, and connection pooling",
            "wrote comprehensive unit and integration tests using PyTest and Mock frameworks"
        ]
    },
    "DevOps Engineer": {
        "skills": [
            "aws", "docker", "kubernetes", "ci/cd", "jenkins", "github actions", "terraform",
            "ansible", "linux", "bash", "prometheus", "grafana", "git", "helm", "nginx"
        ],
        "buzzwords": [
            "provisioned immutable cloud infrastructure across multi-region AWS using Terraform",
            "orchestrated containerized microservices deployments on Kubernetes (EKS) clusters",
            "built automated CI/CD deployment pipelines using GitHub Actions and Jenkins",
            "configured real-time cluster monitoring and automated alerting using Prometheus and Grafana",
            "implemented zero-downtime rolling deployments, SSL termination, and reverse proxies"
        ]
    },
    "Data Analyst": {
        "skills": [
            "sql", "excel", "power bi", "tableau", "python", "pandas", "data visualization",
            "business intelligence", "statistical analysis", "reporting", "etl", "eda"
        ],
        "buzzwords": [
            "authored complex multi-table SQL queries, CTEs, and window functions for reporting",
            "developed automated executive business intelligence dashboards in Power BI and Tableau",
            "performed ad-hoc exploratory data analysis using Python Pandas and Advanced Excel",
            "identified revenue leakages and supply chain bottlenecks through cohort trend analysis",
            "partnered with cross-functional product teams to define key performance indicators (KPIs)"
        ]
    },
    "Cybersecurity Analyst": {
        "skills": [
            "network security", "siem", "wireshark", "vulnerability assessment", "firewalls",
            "penetration testing", "ethical hacking", "incident response", "owasp", "linux",
            "cryptography", "burp suite", "tcp/ip"
        ],
        "buzzwords": [
            "monitored security alerts in enterprise SIEM platform to detect unauthorized intrusion attempts",
            "conducted regular vulnerability assessments and penetration tests across network endpoints",
            "analyzed malicious network packet captures using Wireshark and configured firewall ACLs",
            "led rapid incident response and digital forensics triage following security anomalies",
            "enforced security compliance standards according to OWASP Top 10 and NIST frameworks"
        ]
    },
    "Mobile App Developer": {
        "skills": [
            "flutter", "dart", "react native", "swift", "kotlin", "android studio",
            "mobile app development", "rest api", "firebase", "git", "xcode"
        ],
        "buzzwords": [
            "developed cross-platform mobile applications for iOS and Android using Flutter and Dart",
            "integrated Firebase Cloud Messaging push notifications, Firestore, and authentication",
            "implemented fluid animations, intuitive navigation flows, and offline data persistence",
            "published enterprise mobile applications to Google Play Store and Apple App Store",
            "connected native device sensors, GPS location tracking, and camera capabilities"
        ]
    },
    "Cloud Solutions Architect": {
        "skills": [
            "aws", "azure", "gcp", "cloud computing", "system design", "docker", "kubernetes",
            "microservices", "serverless", "terraform", "network security", "linux"
        ],
        "buzzwords": [
            "architected fault-tolerant, highly available cloud infrastructures across AWS and Azure",
            "designed disaster recovery, multi-region failover, and global load balancing strategies",
            "led enterprise cloud migration initiatives from legacy on-premise servers to serverless",
            "conducted architectural reviews for cost optimization and Well-Architected Framework compliance",
            "collaborated with engineering teams to enforce enterprise security posture and governance"
        ]
    }
}


# Realistic common software engineering responsibilities shared across all roles
COMMON_TASKS = [
    "collaborated with cross-functional engineering teams in agile sprints to deliver production features",
    "authored comprehensive unit tests and participated in peer code reviews to maintain code quality",
    "optimized application performance, identified bottlenecks, and resolved critical production defects",
    "managed git branching workflows, pull requests, and continuous integration pipeline automation",
    "participated in system architecture design reviews and documented technical specifications",
    "interfaced with product managers and stakeholders to translate business requirements into technical solutions",
    "configured logging and monitoring tools to track application health and reliability metrics",
    "managed database connections, indexed tables, and optimized data serialization formats"
]

UNIVERSAL_SKILLS = ["git", "linux", "agile", "docker", "sql", "python", "rest api", "jira"]

# Real-world adjacent domains that naturally share technical overlap
ADJACENT_PAIRS = {
    "Machine Learning Engineer": "Data Scientist",
    "Data Scientist": "Data Analyst",
    "Full Stack Developer": "Frontend Developer",
    "Backend Developer": "Full Stack Developer",
    "DevOps Engineer": "Cloud Solutions Architect",
    "Frontend Developer": "Full Stack Developer",
    "Data Analyst": "Data Scientist",
    "Cloud Solutions Architect": "DevOps Engineer"
}


def generate_synthetic_dataset(samples_per_role: int = 70) -> pd.DataFrame:
    """
    Generate realistic synthetic resume profiles with natural cross-disciplinary
    skill overlaps and shared engineering responsibilities to produce believable,
    academically sound model comparison benchmarks.
    """
    random.seed(42)
    np.random.seed(42)
    rows = []

    intro_templates = [
        "Results-oriented software professional with extensive hands-on experience in high-impact technical environments.",
        "Passionate engineer dedicated to building scalable, robust architectures and delivering performant solutions.",
        "Analytical and detail-oriented technical practitioner with a demonstrated history of driving engineering excellence.",
        "Innovative developer skilled in modern technologies, system design patterns, and cross-functional collaboration.",
        "Adaptable professional with deep technical acumen, strong problem-solving capabilities, and a focus on measurable impact.",
        "Senior technical contributor experienced in designing production systems, optimizing workflows, and mentoring junior engineers.",
        "Motivated engineering graduate with solid computer science fundamentals, quick learning agility, and practical project experience."
    ]

    for role, profile in ROLE_PROFILES.items():
        skills_pool = profile["skills"]
        buzzwords = profile["buzzwords"]

        for i in range(samples_per_role):
            # Select 3 to 5 core domain skills
            cand_skills = random.sample(skills_pool, random.randint(3, min(5, len(skills_pool))))
            # Add 2 to 3 universal skills (git, sql, docker, agile, etc.)
            cand_skills.extend(random.sample(UNIVERSAL_SKILLS, random.randint(2, 3)))

            # 35% chance to include a skill from an adjacent discipline
            if random.random() < 0.35 and role in ADJACENT_PAIRS:
                adj_role = ADJACENT_PAIRS[role]
                cand_skills.extend(random.sample(ROLE_PROFILES[adj_role]["skills"], random.randint(1, 2)))

            cand_skills = list(set(cand_skills))
            skills_str = ", ".join(cand_skills)

            # Combine 1 domain accomplishment + 2 common engineering tasks
            if random.random() < 0.65:
                domain_task = random.choice(buzzwords)
            elif role in ADJACENT_PAIRS and random.random() < 0.8:
                domain_task = random.choice(ROLE_PROFILES[ADJACENT_PAIRS[role]]["buzzwords"])
            else:
                domain_task = random.choice(COMMON_TASKS)

            exp_list = [domain_task] + random.sample(COMMON_TASKS, 2)
            random.shuffle(exp_list)
            exp_str = " ".join(exp_list)

            intro = random.choice(intro_templates)
            resume_text = (
                f"Professional Profile: {intro} "
                f"Core Competencies and Technical Stack: {skills_str}. "
                f"Key Projects and Accomplishments: {exp_str}. "
                f"Consistently applied software engineering best practices, participated in code reviews, and adhered to rigorous testing standards."
            )

            rows.append({
                "text": resume_text,
                "role": role,
                "skills_count": len(cand_skills)
            })

    df = pd.DataFrame(rows)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df


def main():
    print("=" * 60)
    print("Training Job Role Classification Models (LR, SVM, RF, XGBoost)")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    print("Step 1: Generating balanced synthetic resume dataset (700 profiles across 10 roles with natural overlap)...")
    df = generate_synthetic_dataset(samples_per_role=70)
    
    csv_path = os.path.join(data_dir, "resume_training_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved training dataset to: {csv_path}")
    print(f"Dataset shape: {df.shape}")
    print(df['role'].value_counts())

    print("\nStep 2: Training and benchmarking ML models...")
    classifier = JobRoleClassifier()
    metrics = classifier.train_and_compare(df, test_size=0.25, random_state=42)

    print("\n" + "=" * 60)
    print("MODEL COMPARISON RESULTS:")
    print("=" * 60)
    print(f"{'Model Name':<25} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 75)
    for model_name, m in metrics.items():
        print(f"{model_name:<25} | {m['accuracy']:<9}% | {m['precision_weighted']:<9}% | {m['recall_weighted']:<9}% | {m['f1_score_weighted']:<9}%")

    print("=" * 75)
    print(f"Best performing model: {classifier.best_model_name}")
    print("Saved trained model pack to: models/job_role_classifier.pkl")
    print("Saved evaluation metrics to: models/model_metrics.json")
    print("Training successfully completed!\n")


if __name__ == "__main__":
    main()
