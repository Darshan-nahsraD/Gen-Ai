from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
llm = ChatGroq(model="openai/gpt-oss-120b")

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

history=[
    SystemMessage(content = "you are a funny AI agent")
]

print("----------------------------- HELLO!! WHAT'S UP !! HOW CAN I CHANGE YOUR MOOD -----------------------------------")

while(1):
    querry = input("YOU : ")
    if(querry=="exit") : 
        print("Thank you nice to see you again!!!!!!!")
        break
    history.append(HumanMessage(content=querry))

    response=llm.invoke(history)

    history.append(AIMessage(content=response.content))
    print("BOT : ", response.content)
    print()
    print()
    print()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! print exit to stop !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


