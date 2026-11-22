erDiagram
    CATEGORY ||--o{ DISH : contains
    DISH }o--o{ DAILY_MENU : included_in
    ORDER ||--|{ ORDER_ITEM : contains
    DISH ||--o{ ORDER_ITEM : ordered_as

    CATEGORY {
        int id PK
        string name
        text description
    }

    DISH {
        int id PK
        int category_id FK
        string name
        text description
        decimal price
        boolean is_available
    }

    DAILY_MENU {
        int id PK
        date date UK
    }

    ORDER {
        int id PK
        string customer_name
        datetime created_at
        string status
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int dish_id FK
        int quantity
        decimal price
    }