import argparse
import asyncio
from sender import command as send 
from receiver import command as receive 

def main():  
    parser = argparse.ArgumentParser(description="CLI for Service Bus interactions")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # "Send" command updated to use --batches instead of --samples
    parser_send = subparsers.add_parser('send', help="Send events in batches to Service Bus")
    group_send = parser_send.add_mutually_exclusive_group(required=True)
    group_send.add_argument('--topic', type=str, help="Service Bus Namespace & Topic. Format: namespace.topic")
    group_send.add_argument('--queue', type=str, help="Service Bus Namespace & Queue. Format: namespace.queue")
    parser_send.add_argument('--batches', required=True, type=int, default=5, help="Number of concurrent batches to send")

    # "Receive" command (keeps the previous continuous reading update)
    parser_receive = subparsers.add_parser('receive', help="Receive events from Service Bus")
    group_receive = parser_receive.add_mutually_exclusive_group(required=True)
    group_receive.add_argument('--topic', type=str, help="Namespace, Topic & Subscription. Format: namespace.topic.subscription")
    group_receive.add_argument('--queue', type=str, help="Service Bus Namespace & Queue. Format: namespace.queue")

    args = parser.parse_args()
   
    if args.command in ['send', 'receive']:
        target_str = args.topic if args.topic else args.queue
        parts = target_str.split(".")
        
        if args.command == 'receive' and args.topic:
            if len(parts) != 3:
                parser_receive.error("For receiving from a topic, format must be exactly: namespace.topic.subscription")
            
            namespace = parts[0]
            entity_name = parts[1]
            subscription = parts[2]
        else:
            if len(parts) != 2:
                param_used = '--topic' if args.topic else '--queue'
                parser.error(f"Format for {args.command} with {param_used} must be exactly: namespace.entity_name")
            
            namespace = parts[0]
            entity_name = parts[1]
            subscription = None

        if args.command == 'send':
            asyncio.run(send(
                namespace=namespace,
                topic=entity_name if args.topic else None,
                queue=entity_name if args.queue else None,
                batches=args.batches
            ))
            
        elif args.command == 'receive':
            asyncio.run(receive(
                 namespace=namespace,
                 topic=entity_name if args.topic else None,
                 queue=entity_name if args.queue else None,
                 subscription=subscription
            ))
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()