from cyberfusion.RabbitMQConsumerLogServer import database, seeders

database_session = database.make_database_session()

rpc_request_logs = seeders.seed_rpc_request_logs(database_session)
seeders.seed_rpc_response_logs(database_session, rpc_request_logs)
