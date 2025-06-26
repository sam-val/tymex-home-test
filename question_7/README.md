# System Design Challenge: Multi-Channel Notification System

## 📚 Table of Contents

- [❗ Introduction](#introduction)
- [🧰 Techstack](#️-tech-stack)
- [🗺️ High-Level Diagram](#high-level-diagram)
- [🧩 Main APIs](#main-apis)
- [🗃️ Database Schema](#database-schema)
- [🎯 Priority Levels](#priority-levels-via-kafka-topics)
- [🔁 Retry Mechanism](#retry-kafka-topics-by-channel--delay-tier)
- [🚦 Rate Limiting](#rate-limiting)
- [📬 Delivery Status Tracking](#delivery-status-tracking)
- [⚙️ Availability & Scalability](#availability--scalability)
- [🛡️ Fault Tolerance & Graceful Degradation](#fault-tolerance-and-graceful-degradation)


## Introduction

### Problem

```
You are tasked with designing a notification system for a large-scale application. The system needs to
support multiple notification channels (email, SMS, push notifications) with different priority levels. The
system should be scalable, reliable, and able to handle high volumes of notifications.
```

Since we want to make a notification system for an existing large-scale app. I intend to make the system to be a **dedicated microservice**.

Let's try to solve each of the requirements, **you can click on each requirement to quickly jump to the answer**:

### Functional Requirements:
1. [Support multiple notification channels](#multi-channel-support-email-sms-push-in-app)
2. [Implement priority levels for notifications (e.g., critical, high, medium, low)](#primary-notification-topics-by-priority)
3. [Allow users to set preferences for notification channels based on notification types](#update-preferences-api)
4. [Support throttling and rate limiting to prevent notification spam](#rate-limiting)
5. [Provide delivery status tracking (sent, delivered, failed, read)](#delivery-status-tracking)
6. [Handle notification retries for failed deliveries with configurable retry policies](#retry-kafka-topics-by-channel--delay-tier)

### Non Functional Requirements:
1. [High availability (99.9% uptime)](#availability--scalability)
2. [Scalability to handle millions of notifications per day](#availability--scalability)
3. [Low latency for high-priority notifications](#primary-notification-topics-by-priority)
4. [Fault tolerance and graceful degradation](#fault-tolerance-and-graceful-degradation)
5. [Support for future expansion to additional notification channels](#️-easily-extensible-for-future-channels)

## ⚙️ Tech Stack

- **Cloud Provider**: AWS (or aligned with that of the core application's)
- **API Server**: FastAPI (asynchronous, lightweight, Python-based)
- **Message Broker**: Apache Kafka (high-throughput, distributed messaging)
- **Datastores**:
  - **PostgreSQL** – primary relational database
  - **Redis** – caching layer and delay queue (e.g., for retries or throttling)
- **Notification Channels**:
  - **Email**: SendGrid
  - **SMS**: Twilio
  - **Push Notifications**: Firebase Cloud Messaging (FCM)
  - **In-App**: Internal storage + API/WebSocket delivery
- **Monitoring & Observability**:
  - **Metrics**: Prometheus + Grafana
  - **Error Tracking**: Sentry / Datadog
  - **Logging**: Grafana Loki (structured log aggregation)

## High Level Diagram

![high level diagram](https://github.com/user-attachments/assets/4c67e4a6-732c-4d6d-9b5b-dbf254528f93)


## Main APIs 

### Make notification

<details>
 <summary><code>POST</code> <code><b>/api/notification/v1/notifs/</b></code>

 <code>(Make a notification)</code></summary>

##### Payload

> | name     | type     | data type | description          | example            |
> | -------- | -------- | --------- | -------------------- | ------------------ |
> | user_id | required | uuid     | id of user   | fec604061ef14b0dac927ef8e70f2ff0           |
> | notif_type | required | str       | notification type              | sms |
> | message | required | str       |  should not be empty, can add length limit              | Bank account has been topped-up $100! |
> | priority | required | str       | high/medium/low              | high |

##### Responses

> | http code | content-type       | response                       |
> | --------- | ------------------ | ------------------------------ |
> | `200`     | `application/json` | `{ "data": { "message": "accepted" },`  |


</details>

### Update preferences API

<details>
 <summary><code>PUT</code> <code><b>/api/notification/v1/user/preferences/</b></code>

 <code>(Update user's preferences config)</code></summary>

##### Payload Example

```json
{
  "user_id": "fec604061ef14b0dac927ef8e70f2ff0",
  "preferences": [
    {
      "notification_type": "order_status",
      "channel": "email",
      "enabled": true
    },
    {
      "notification_type": "order_status",
      "channel": "sms",
      "enabled": false
    },
    {
      "notification_type": "security_alert",
      "channel": "push",
      "enabled": true
    }
  ]
}
```

##### Responses

> | http code | content-type       | response                       |
> | --------- | ------------------ | ------------------------------ |
> | `200`     | `application/json` | `{ "data": { "message": "updated" },`  |

</details>

The update is stored on Postgres. [Schema is below](#table-user_notification_preferences)


### (optional) Get Notifications (for inapp notif)

<details>
 <summary><code>GET</code> <code><b>/api/notification/v1/user/{user_id}/notifs/</b></code>

 <code>(Get notification history)</code></summary>

</details>

## Database schema

Tables are on Postgres, can be cached with Redis for enhancement

### Table: user_notification_preferences


```sql
CREATE TABLE user_notification_preferences (
    user_id UUID NOT NULL,
    notification_type TEXT NOT NULL,
    channel TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (user_id, notification_type, channel)
);
```
Example:

| user\_id | notification\_type | channel  | enabled |
| -------- | ------------------ | -------- | ------- |
| 101      | order\_status      | email    | true    |
| 101      | order\_status      | sms      | false   |
| 101      | order\_status      | push     | true    |
| 101      | security\_alert    | sms      | true    |
| 101      | security\_alert    | whatsapp | true    |

### Table: feature_setting

We can make a centralized one like below.

Like a centralized setting. One JSON field is enough. Content could be something like:

```sql
CREATE TABLE feature_settings (
    feature_name TEXT PRIMARY KEY,
    config JSONB,
    enabled BOOLEAN DEFAULT TRUE
```

Example:

| feature_name | config  | enabled |
| -------- | -------- | ------- |
| notification      |json    | true    |

```json
{
  "retry_settings": {
    "sms": {
      "max_attempts": 3,
      "initial_backoff_seconds": 30,
      "backoff_strategy": "exponential",
      "max_backoff_seconds": 300,
      "retry_enabled": true
    },
    "email": {
      "max_attempts": 5,
      "initial_backoff_seconds": 10,
      "backoff_strategy": "fixed",
      "max_backoff_seconds": 60,
      "retry_enabled": true
    }
  },
  "other_settings": {
    "throttle_per_user_per_minute": 5,
  }
}
```

### Table: notification_status_tracking

Quick schema idea for tracking the notif status

```sql
CREATE TABLE notification_status_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    notif_type TEXT NOT NULL,
    channel TEXT NOT NULL,
    status TEXT NOT NULL,  -- e.g., 'sent', 'delivered', 'failed', 'read'
    attempt INT DEFAULT 0,
    retry_time TIMESTAMP,
    provider_msg_id TEXT,
    message JSONB,  -- can be TEXT also
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

| id        | user\_id                               | notif\_type     | channel | status    | attempt | retry\_time         | provider\_msg\_id | message                                                           | created\_at         | updated\_at         |
| --------- | -------------------------------------- | --------------- | ------- | --------- | ------- | ------------------- | ----------------- | ----------------------------------------------------------------- | ------------------- | ------------------- |
| `b1a2...` | `fec60406-1ef1-4b0d-ac92-7ef8e70f2ff0` | order\_status   | email   | sent      | 0       | `NULL`              | sg\_abc123        | {"subject": "Order shipped", "body": "Your order is on the way."} | 2025-06-25 10:00:00 | 2025-06-25 10:00:00 |
| `b1a3...` | `fec60406-1ef1-4b0d-ac92-7ef8e70f2ff0` | order\_status   | sms     | failed    | 1       | 2025-06-25 10:30:00 | tw\_456def        | {"text": "Order shipped"}                                         | 2025-06-25 10:00:00 | 2025-06-25 10:05:00 |
| `b1a4...` | `fec60406-1ef1-4b0d-ac92-7ef8e70f2ff0` | security\_alert | push    | delivered | 0       | `NULL`              | fcm\_9988ff       | {"title": "Login alert", "device": "iPhone", "ip": "1.2.3.4"}     | 2025-06-25 08:30:00 | 2025-06-25 08:31:00 |
| `b1a5...` | `fec60406-1ef1-4b0d-ac92-7ef8e70f2ff0` | promo           | email   | read      | 0       | `NULL`              | sg\_987zyx        | {"subject": "50% off today!", "campaign\_id": "promo2025"}        | 2025-06-24 20:00:00 | 2025-06-24 21:15:00 |


## Multi-Channel Support (Email, SMS, Push, In-App)

Create a `BaseChannel` abstract class with methods like:

```python
class BaseChannel:
    async def send(self, notification_payload: dict) -> NotificationResult:
        raise NotImplementedError
```

- Each channel (EmailChannel, SMSChannel...) inherits and implements send

- Workers pick the right channel class based on user preferences + notification type

### ✔️ Easily extensible for future channels.

Whenever we want to add new channel. Just add new channel config in [feature setting](#table-feature_setting)

Then implement the logic for `send`

## Priority Levels via Kafka Topics

Kafka is a distributed message broker with a topic-based publish-subscribe system.
It's designed for high throughput, durability, and scalability — making it ideal for large-scale, event-driven systems.

Say we have these topics:

### Primary Notification Topics by Priority

| Priority | Topic Name               |
| -------- | ------------------------ |
| Critical | `notifications.critical` |
| High     | `notifications.high`     |
| Medium   | `notifications.medium`   |
| Low      | `notifications.low`      |

Each topic is mapped to a consumer in the same group level (`worker-high` with `notifications-high`)

Setting could be like this, workers with higher priority have higher stats:

| Env  | Worker            | Replicas | CPU Priority |
| ---- | ----------------- | -------- | ------------ |
| Prod | `worker-critical` | 5        | High         |
| Prod | `worker-high`     | 3        | Normal       |
| Prod | `worker-low`      | 1        | Low          |

With this topic structure, it allows critical & high priority notifications to have low latency since there is more resources on the import workers. We can easily scale horizonally.


## Retry Kafka Topics by Channel + Delay Tier

We can use kafka consumers to retry, here is one way to approach it using same workers as the priority workers. Mapping topics to them like so:

| Topic                    | Handled By        | Notes                      |
| ------------------------ | ----------------- | -------------------------- |
| `notifications.critical` | `worker-critical` | Fresh critical notifs      |
| `retry.*.30s`            | `worker-critical` | First retry (short delay)  |
| `notifications.high`     | `worker-high`     | Fresh high-priority notifs |
| `retry.*.2m`             | `worker-high`     | Medium retry               |
| `notifications.low`      | `worker-low`      | Fresh low-priority notifs  |
| `retry.*.10m`            | `worker-low`      | Long retry (low priority)  |


### 🔧 Example Typical Retry Flow
1. A message fails to send via email.

2. The system calculates retry delay (say, 30s for attempt #1).

3. It publishes the message to `retry.email.30s`

4. A retry worker is listening to this topic.

5. That worker:

- May delay consumption (sleep 30s), or

- May immediately process if delay already passed

If it fails again, it may be sent to topics: `retry.email.2m` -> `retry.email.10m` → `dead-letter` (final stop)

### Extra: Delay Manager (Polling Service) 

The problem when doing retry with delay is when we do `sleep()`. It's rather wasteful with our resources. We can use a delay manager to enhance this:

1. When a notification/task fails, we (consumers/workers) does not retry immediately.

2. Instead, it adds the failed message to a Redis ZSET, with value `ready_at`:
```python
# Example: Add failed email message to retry queue
redis.zadd("retry_queue:email", {json.dumps(payload): ready_at})
```

3. Then a separate async service (called the Delay Manager) runs in a loop:

- Every few seconds, it queries Redis ZSET for all messages with ready_at <= now

- For each ready message:

    - Sends it back to the original Kafka topic (e.g., notifications.high)

    - Removes it from the ZSET to avoid reprocessing

Downside is messsages are bounced back and forth. But it's still ok.


## Rate limiting

Since this is an internal microservice. No need to throttle external IPs in the network layer, but we can throttle API in the app layer, based on the `user_id` for example.

Can use Redis to throttle is an option, e.g. creating a key for user_id 123 for email channel, `user:123:email:count`, can set TTL (time to live) any amount.

Refused request if it's exceed a certain threshold configs, which can be put in [feature setting](#table-feature_setting).

## Delivery status tracking
Since there might be millions/billions of notifications in total. It's not wise to store all rows of them on a SQL database forever. But if logging is not enough and we have real-time usage of the delivery status. We can store on Postgres, and purge them every 14-30 days.

For the SQL schema, check the a quick example [here](#table-notification_status_tracking)

| Component                   | Role                                               |
| --------------------------- | -------------------------------------------------- |
| **PostgreSQL**              | Store delivery statuses for 14–30 days              |
| **Redis**                   | Cache recent statuses (1–2 hours) for quick access |
| **Auto-purge**              | Drop old data beyond 14 days (via partitions)      |
| **S3 / Parquet** | Archive for long-term analytics                    |
| **Athena** | Query for analytics                    |

## Availability & Scalability

We can deployed on AWS ECS/EKS with ALB + health checks to maintain availability.

For scaling we can use AWS EC2 auto Scaling. One for the producers, one for the consumers.

- Kafka Producers: Can scale based on throughput (request rate or CPU usage)
- Kafka Consumers: Can scale based on Kafka consumer lag or queue depth

```
┌────────────────────────────┐
│     Core Application       │
└────────────┬───────────────┘
             │
             ▼
     ┌────────────────┐
     │ Load Balancer  │ (ALB/NLB)
     └────┬────┬──────┘
          │    │
          ▼    ▼
┌────────────────────────────┐
│    ASG: Kafka Producers    │  ← FastAPI (async) apps
│ (e.g., POST /notif)        | 
└────────────┬───────────────┘
             │ (send msg to Kafka)
             ▼
     ┌────────────────┐
     │ Kafka Brokers  │ (MSK or Self-hosted)
     └────┬────┬──────┘
          │    │
          ▼    ▼
┌────────────────────────────┐
│    ASG: Kafka Consumers    │ ← FastAPI or worker apps
│ (process + send via SDKs)  │
└────────────┬───────────────┘
             ▼
  ┌──────────────────────────────────────┐
  │ External Providers:                  │
  │ Sendgrid (Email), Twilio (SMS)       │
  └──────────────────────────────────────┘
```

## Fault tolerance and graceful degradation

With this system, we can have a high level of fault tolerance.

Scenarios when things go wrong --

| Component        | What Can Go Wrong       | Fault Tolerance Strategy                            |
| ---------------- | ----------------------- | --------------------------------------------------- |
| Kafka broker     | Broker node fails       | Kafka auto reassigns partitions to healthy brokers  |
| Kafka consumer   | Crashed worker          | Another worker picks up the partition (same group)  |
| Email/SMS APIs   | Third-party outage      | Use retries, fallback channels, or log and continue |
| Redis (throttle) | Cache down              | Skip rate check or apply a default limit            |
| DB (status logs) | Temp connection fail    | Retry w/ exponential backoff or write to buffer/log |
| API overload     | Spike of notif requests | Auto-scale producers, queue requests, return 202    |
