# JEMVote

jemvote.io/a1

## Development Phases

* Phase 1
  * Manually close poll
* Phase 2
  * Add Expiration date to automatically close the poll
  * Restrict voters
  * Add description to poll
  * Allow voters to change their vote

## API

### Create/manage a Poll

```text
POST /api/polls
Headers:
  Authorization: Bearer <JWT>
Body:
  {
    "name": "My Great Poll"
  }
```

```text
GET /api/polls/<poll_id>
Headers:
  Authorization: Bearer <JWT>
Body:
  {
    "id": "123abc",
    "short_id": "a1",
    "user_id": "123abc",
    "name": "My Great Poll",
    "created_date": "2019...",
    "status": "unpublished",
    "candidates": []
  }
```

```text
PATCH /api/polls/<poll_id>
Headers:
  Authorization: Bearer <JWT>
Body:
  {
    "name": "My Great Poll",
    "status": "published",
    "candidates": ["option1", "option2"]
  }
```

```text
DELETE /api/polls/<poll_id>
Headers:
  Authorization: Bearer <JWT>
Body:
  <none>
```

### Vote API

```text
POST /api/polls/<poll_id>/votes
Headers:
  Authorization: Bearer <JWT>
Body:
  {
    "candidates": ["option2", "option1"]
  }
```

```text
GET /api/polls/<poll_id>/votes/<vote_id>
Headers:
  Authorization: Bearer <JWT>
Body:
  {
    "id": "123abc",
    "user_id": "123abc",
    "created_date": "2019...",
    "candidates": ["option2", "option1"]
  }
```

### Auth API


### Result API

```text
GET /api/polls/<poll_id>/results
Headers:
  Authorization: Bearer <JWT>
Body:
  {
    "phases": [
      [{
        "name": "option1",
        "votes": 10,
        "active": true
      },{
        "name": "option2",
        "votes": 10,
        "active": true
      },{
        "name": "option3",
        "votes": 1,
        "active": false
      }], [{
        "name": "option1",
        "votes": 10
        "active": false
      },{
        "name": "option2",
        "votes": 11,
        "majority": true
      }]
    ]
  }
```