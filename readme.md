# Rwanda App

Rwanda is an innovative digital platform serving as a marketplace for both sellers and buyers, offering a
seamless experience for trading digital products. The name **Rwanda** is a code name inspired by the country
**[Rwanda](https://en.wikipedia.org/wiki/Rwanda)** in Africa, this project aims to foster economic growth and
empowerment by facilitating transactions in the
digital realm. Sellers can showcase their digital creations, while buyers can explore a diverse range of products,
creating a dynamic marketplace that celebrates creativity and entrepreneurship. With Rwanda, the digital landscape
becomes more accessible, connecting individuals and businesses worldwide in a thriving ecosystem of trade and
innovation.

## Online Demo

Feel free to try it out. Check the credentials below.

### Account

[https://rwanda.danielblandes.com](https://rwanda.danielblandes.com)

- Seller
  - seller@rwanda.app
  - sellerpassword

- Buyer John
  - john@rwanda.app
  - johnpassword

- Buyer Jane
  - jane@rwanda.app
  - janepassword

### Admin

[https://admin.rwanda.danielblandes.com](https://admin.rwanda.danielblandes.com)

- Superuser
  - superuser@rwanda.app
  - superuserpassword

### App (Backend)

- GraphQl Account - [https://app.rwanda.danielblandes.com/graphql/](https://app.rwanda.danielblandes.com/graphql/)
- GraphQl
  Admin - [https://app.rwanda.danielblandes.com/graphql-admin/](https://app.rwanda.danielblandes.com/graphql-admin/)

## Key Features

* **Seller Portfolio**: Allow sellers to showcase their portfolio, previous work.

* **Service Categories and Filters**: Organize services into categories and provide filters to allow users to easily
  find what they're looking for based on their preferences and requirements.

* **Service Selection**: Users should be able to browse through a variety of services offered by different sellers, with
  detailed descriptions, pricing, and seller ratings.

* **Order Placement**: Allow users to easily place orders for services they wish to avail. This should include options
  for customization, if applicable.

* **Secure Messaging**: Implement a built-in chat feature with online status that enables seamless communication between
  the buyer and the seller. This ensures clarity regarding the service requirements, delivery details, and any other
  queries.

* **Delivery Tracking**: Provide users with real-time updates on the status of their service delivery.

* **Payment Escrow**: Utilize an escrow system to hold the payment securely until the service is successfully delivered.
  This builds trust between the buyer and the seller, as the seller knows they will only receive payment upon completion
  of the service.

* **Seller Verification**: Implement a verification process for sellers to ensure they are legitimate and trustworthy.
  This
  can involve identity verification and verifying the quality of their services.

* **Resolve Disputes** feature empowers administrators to efficiently and fairly handle any conflicts or disputes that
  may arise between buyers and sellers on the platform. It provides a structured process for reviewing, investigating,
  and reaching resolutions for disputed transactions.

* **Multi-platform Accessibility**: Ensure the app is accessible across various devices and platforms, including
  smartphones, tablets, and desktops, to maximize user convenience.

* **Development & Deployment**: Rwanda utilizes Docker containers to streamline its development and deployment
  processes, bolstering the efficiency and consistency of its backend and frontend applications.

## Architecture

The application architecture is split in three different parts: app(backend), frontend for seller and buyer accounts,
and frontend for admins

### App (Backend With Django Framework)

The backend of the application serves as the central component responsible for managing data, handling business logic,
and facilitating communication between the frontend interfaces and the database. Here's a breakdown of its key
components

- **Server**: Built on top of a high-level [Python](https://docs.python.org/3.9/) web
  framework [Django](https://docs.djangoproject.com/en/3.2).

- **Database**: Utilized the World's most advanced open source relational
  database [PostgreSQL](https://www.postgresql.org/docs/16/index.html) to store user information, service details,
  orders, and chat messages.

- **API Endpoint**: Take advantage of [Graphql](https://graphql.org) using the
  package [Graphene Django](https://docs.graphene-python.org/projects/django/en/latest) to handle operations such as
  user authentication, service listing, order placement, messaging between users, and payment processing.

- **Authentication**: Implement strong and secure authentication and authorization mechanisms
  using [Django GraphQL JWT](https://django-graphql-jwt.domake.io/) witch is a JSON Web Token (JWT) authentication for
  [Graphene Django](https://docs.graphene-python.org/projects/django/en/latest).

- **Websockets**: Integrate Websockets for real-time communication between buyers and sellers during the chat exchange
  using [Django Channels based WebSocket](https://github.com/datadvance/DjangoChannelsGraphqlWs)
  for [Graphene Django](https://docs.graphene-python.org/projects/django/en/latest).

- **Payment Gateway Integration**: Integrate [CinetPay](https://cinetpay.com) a mobile money payment gateway to
  facilitate secure payment transactions between buyers and sellers.

- **Background Jobs**: Implement background job processing using [Celery](https://docs.celeryq.dev/en/stable/index.html)
  and [Redis](https://redis.com) to handle tasks such as sending notifications, updating order status, and processing
  payments asynchronously.

### Account (Vue Framework)

The frontend interfaces for sellers and buyers provide user-friendly interfaces for browsing services, placing orders,
and managing their accounts. Here are the technical details:

- **Framework**: Develop the frontend using a modern JavaScript framework [Vue.js 2](https://v2.vuejs.org/v2/guide) to
  create dynamic and responsive user interfaces.

- **Component Architecture**: Organize the frontend application into reusable components for modularity and
  maintainability.

- **State Management**: Utilize state management [Vuex](https://vuex.vuejs.org) to manage application state, including
  user
  authentication, service listings, and order status.

- **API Integration**: Communicate with the backend API endpoints using asynchronous HTTP requests
  using [Vue Apollo 3](https://apollo.vuejs.org/guide) to fetch service data, submit orders, and exchange messages.

- **Real-time Updates**: Implement real-time updates using Websockets to display new messages and order status changes
  without the need for manual page refreshes.

- **Responsive Design**: Ensure the frontend interfaces are optimized for various screen sizes and devices using
  responsive design principles and CSS
  frameworks [Bootstrap 4](https://getbootstrap.com/docs/4.6/getting-started/introduction).

### Admin (Vue Framework)

The frontend interface for admins provides the necessary tools for managing users, services, orders, and resolving
disputes. Here are the technical aspects:

- **Framework**: Develop the frontend using a modern JavaScript framework [Vue.js 2](https://v2.vuejs.org/v2/guide) to
  create dynamic and responsive user interfaces.

- **Component Architecture**: Organize the frontend application into reusable components for modularity and
  maintainability.

- **State Management**: Utilize state management [Vuex](https://vuex.vuejs.org) to manage application state, including
  user authentication, disputes details.

- **API Integration**: Communicate with the backend API endpoints using asynchronous HTTP requests
  using [Vue Apollo 3](https://apollo.vuejs.org/guide) to fetch service data, submit orders, and exchange messages.

- **Real-time Updates**: Implement real-time updates using Websockets to display new messages and order status changes
  without the need for manual page refreshes.

- **Responsive Design**: Ensure the frontend interfaces are optimized for various screen sizes and devices using
  responsive
  design principles and CSS frameworks [Bootstrap 4](https://getbootstrap.com/docs/4.6/getting-started/introduction).

## Requirements

- [Docker](https://docs.docker.com/install)

## Setup

This repository is composed of three git submodules for each part.

- Clone the repository

```bash
git clone git@gitlab.com:rwanda/rwanda-platform.git --recurse-submodules
```

- Build the application

```bash
docker compose build
```

- Update environments variable

```bash
cp app/.env.example app/.env && cp account/.env.example account/.env && cp admin/.env.example admin/.env
```

### App

- Make migrations

```bash
docker compose run --rm app python manage.py makemigrations
```

- Run migrations

```bash
docker compose run --rm app python manage.py migrate
```

- Seed data

```bash
docker compose run --rm app python manage.py seed
```

- Create superuser

```bash
docker compose run --rm app python manage.py longbowou root root
```

### Run

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d app
```

## Where is the application running?

- GraphQl Account - [http://localhost:8000/graphql/](http://localhost:8000/graphql/)
- GraphQl Admin - [http://localhost:8000/graphql-admin/](http://localhost:8000/graphql-admin/)
- PgAdmin - [http://localhost:5050](http://localhost:5050)
  - postgres@postgres.app
  - postgres

### What's next ?

Check other parts on [Rwanda Platform](https://gitlab.com/rwanda/rwanda-platform) repository

## License

This project is licensed under the [MIT License](LICENSE).