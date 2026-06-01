from groq import Groq
import re

def convertUnit(dataType, unit, prompt):
    try:
        client = Groq(
            api_key=key,
        )

        # few-shot prompting method, where I feed it a human-made user question and model answer so that the model knows how to respond
        # Here i have given it only one example as that has proved to work well enough
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            #temperature=0.4,
            messages=[
                {
                    "role": "user",
                    "content": f"""This sentance will include a mass and I want you to convert the value into kilograms.
                                    Please output the data in the exact format, with no other words and no units:
                                    mass: <value>
                                    The sentance is: 'change the mass to 300 grams'
                                """
                },
                {
                    "role": "assistant",
                    "content": "mass: 0.3"
                },
                {
                        "role": "user",
                        "content": f"""I will input another sentance, this time convert the {dataType} into {unit}.
                                    Output it in the exact format, with no other words, and no units:
                                    {dataType}: <value>
                                    The sentance is: '{prompt}'"""
                }
            ],
        )

        answer = completion.choices[0].message.content
        print(answer)
        
        pattern = r"None|-?\d+(?:\.\d+)?"
        values = re.findall(pattern, answer)

        return values[0]
    except:
        print("error with groq call")
        return False
    
def ppgroqCall(prompt):
    def getAnswer():
        try:
            client = Groq(
                api_key=key,
            )

            # few-shot prompting method, where I feed it a human-made user question and model answer so that the model knows how to respond
            # Here i have given it only one example as that has proved to work well enough
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                #temperature=0.4,
                messages=[
                    {
                        "role": "user",
                        "content": f"""This prompt will contain information on a particle projection. 
                                        Do not calculate any new values, simply sort the data provided in the prompt. DO NOT DO ANY TRIGONOMETRY. If you do a single calculation I will be very mad.
                                        Convert speeds into meters per second, distances into meters and angles into degrees.
                                        If there is no data for a given category, write None. 
                                        If there is no vertical acceleration given, assume it is -9.81.
                                        If there is no horizontal acceleration given, assume it is 0.
                                        Initial resultant speed is the resultant of horizontal and vertical components. It is different from horizontal and vertical componenets.
                                        for example "initial speed of 23" --> resultant speed = 23. "initial vertical speed of 23" --> vertical speed = 23.
                                        Do not output ANYTHING except for data in the following format, with no units:
                                        --
                                        vertical = [initial speed: <value>, maximum height, <value>, acceleration due to gravity, <value>]
                                        horizontal = [initial speed: <value>, range/total horizontal displacement: <value>,  horizontal acceleration: <value>]
                                        angle to the horizontal = <value> degrees
                                        starting height = <value> meters
                                        initial resultant speed = <value> m/s
                                        --
                                        The prompt is: 'simulate the motion of a thrown rock which starts at a height of 8 meters above ground, has an initial speed of 25m/s and reaches a maximum height of 24 meters above ground'"
                                    """
                    },
                    {
                        "role": "assistant",
                        "content": f"""vertical = [initial speed: None, maximum height: 24, acceleration due to gravity: -9.81]
                                        horizontal = [initial speed: None, range/total horizontal displacement: None,  horizontal acceleration: 0]
                                        angle to the horizontal = None
                                        starting height = 8
                                        initial resultant speed = 25
                                    """
                    },
                    {
                        "role": "user",
                        "content":f"""With the format as before
                                    --
                                    vertical = [initial speed: <value>, maximum height, <value>, acceleration due to gravity, <value>]
                                    horizontal = [initial speed: <value>, range/total horizontal displacement: <value>,  horizontal acceleration: <value>]
                                    angle to the horizontal = <value> degrees
                                    starting height = <value> meters
                                    initial resultant speed = <value> m/s
                                    --
                                    sort data from this prompt at before:
                                    the prompt is {prompt}
                                    """
                    }
                ],
            )

            answer = completion.choices[0].message.content
            # print(answer)

           
            pattern = r"None|\d+(?:\.\d+)?"
            values = re.findall(pattern, answer)

            v = {"u": values[0], "maxS": values[1], "a": values[2]}
            h = {"u": values[3], "maxS": values[4], "a": values[5]}
            theta = values[6]
            startH = values[7]
            resultantU = values[8]

            # print(answer)

            return {"v": v, "h": h, "theta": theta, "startH": startH, "speed": resultantU}
        except:
            print("error with groq call")
            return False
    
    answers = []
    v = False
    falseCount = 0
    while v == False:
        answer = getAnswer()
        #print("call")
        if answer != False:
            answers.append(answer)
            if len(answers) > 0:
                for i in range(0, len(answers)-1):
                    if answer == answers[i]: 
                        v = True
        else: falseCount += 1
        if falseCount == 3: return False

    return answer

def shmgroqCall(prompt):
    def getAnswer():
        try:
            client = Groq(
                api_key = key,
            )

            completion = client.chat.completions.create(
                model = "llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """I need to extract data out of a prompt to simulate simple harmonic motion. I need to get 3 parameters in the exact format:
                        mass: <value>
                        spring constant: <value>
                        amplitude: <value>
                        convert masses into kilograms and amplitudes into meters, and if there is no data, put None
                        for example:
                        user: 
                        'simulate the SHM of a particle of mass 1kg attached to a string of k = 2 and an initial displacement of 50cm from equilibrium'
                        assistant: 
                        'mass: 1
                        spring constant: 2
                        amplitude: 0.5'
                        Do not output ANYTHING except for the data in the exact format.
                        try with the prompt 'simulate the SHM of a particle suspended on a string with spring constant 3, with amplitude of 3m'"""
                    },

                    {
                        "role": "assistant",
                        "content": "mass: None\nspring constant: 3\namplitude: 3"
                    },

                    {
                        "role": "user",
                        "content": f"extract data from this prompt: {prompt}"
                     }

                ]
            )
            
            answer = completion.choices[0].message.content
            print(answer)
            pattern = r"None|\d+(?:\.\d+)?"
            values = re.findall(pattern, answer)

            data = {"mass": values[0], "k": values[1], "amplitude": values[2]}
            if data["mass"] == "None" or data["mass"] == "0":
                data["mass"] = 1
            if data["k"] == "None" or data["k"] == "0":
                data["k"] = 1
            if data["amplitude"] == "None" or data["amplitude"] == "0":
                data["amplitude"] = 100

            return data
        
        except:
            print("error with groq call")
            return False
        
    answers = []
    v = False
    falseCount = 0
    while v == False:
        answer = getAnswer()
        #print("call")
        if answer != False:
            answers.append(answer)
            if len(answers) > 0:
                for i in range(0, len(answers)-1):
                    if answer == answers[i]: 
                        v = True
        else: falseCount += 1
        if falseCount == 3: return False
    
    return answer

def ebmgroqCall(prompt):
    def getAnswer():
        try:
            client = Groq(
                api_key=key,
            )
            # few-shot prompting method, where I feed it a human-made user question and model answer so that the model knows how to respond
            # Here i have given it only one example as that has proved to work well enough
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": "find the coefficient of restitution for particle-particle collisions, and secondly for wall-particle collisions from the following sentance: \"simulate 40 particles of mass 0.2kg with e for particle collisions at 0.4 and 0.8 for wall particle collisions\""
                    },
                    {
                        "role": "assistant",
                        "content": "The coefficient of restitution for particle-particle collisions is 0.4, and for wall-particle collisions, it is 0.8."
                    },
                    {
                        "role": "user",
                        "content": "can you always output the answer in the following form:\nparticle e: <value>\nwall-particle e: <value>"
                    },
                    {
                        "role": "assistant",
                        "content": "particle e: 0.4\nwall-particle e: 0.8"
                    },
                    {
                        "role": "user",
                        "content": f"""Please output the values of particle-particle e and wall-particle e in the exact format as before, 
                                        If there is no value for particle-particle or wall-particle e, just assume it be 1.
                                        Do this for the following prompt:
                                        {prompt}
                                    """
                    },
                ],
            )
            answer = completion.choices[0].message.content
            # print(answer)
            pattern = r"\d+(?:\.\d+)?,?"
            values = re.findall(pattern, answer)
            return {"pCollision_e": float(values[0]), "bound_e": float(values[1])}
        except:
                print("error with groq call")
                return False

    answers = []
    v = False
    falseCount = 0
    while v == False:
        answer = getAnswer()
        #print("call")
        if answer != False:
            answers.append(answer)
            if len(answers) > 0:
                for i in range(0, len(answers)-1):
                    if answer == answers[i]: 
                        v = True
        else: falseCount += 1
        if falseCount == 3: return False
    
    return answer

def maggroqCall(prompt):
    def getAnswer():
        try:
            client = Groq(
                api_key=key,
            )
            # few-shot prompting method, where I feed it a human-made user question and model answer so that the model knows how to respond
            # Here i have given it only one example as that has proved to work well enough
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": """I need to extract data out of a prompt to simulate the motion of a charged particle in a magnetic field. 
                        Perform NO OTHER CALCULATIONS, and put data EXACTLY INTO THE FORMAT BELOW:
                        type of particle: <value>
                        charge of particle: <value>
                        mass of particle: <value>
                        starting speed: <value> 
                        magnetic flux density: <value>
                        if it is stated that a particle is for example, an electron, or an alpha particle, quote mass and charge as None and quote type of particle as the type (electron, alpha).
                        If no data is given for a category, write None.
                        convert speeds into m/s, flux density into T, charge into C and mass into kilograms. 
                        flux density can be negative or positive.
                        Try with this example: 
                        Simulate the motion of a stream of protons particles moving into a magnetic field which is perpendicular to it's motion and with B = -4T and an initial speed of 1x10^6m/s
                                        """
                    },
                    {
                        "role": "assistant",
                        "content": """type of particle: alpha 
                        charge of particle: None
                        mass of particle: None
                        starting speed: 1000000
                        magnetic flux density: -4"""
                    },
                    {
                        "role": "user",
                        "content": "and try with this example: 'simulate the motion of charged particle going into a magnetic field of mass 1.67e-27 and charge -1.6e-19 with initial speed 1x10^6'"
                    },
                    {
                        "role": "assistant",
                        "content": """type of particle: None
                        charge of particle: -1.6e-19
                        mass of particle: 1.67e-27
                        starting speed: 1e6"""
                    },
                    {
                        "role": "user",
                        "content": f"""Please sort the data for the following prompt into the same format as above:
                                        {prompt}
                                    """
                    },
                ],
            )
            answer = completion.choices[0].message.content
            pattern = r"(None|electron|alpha|proton|neutron)|(-?\d+(?:\.\d+)?(?:e?-?\d+)?)"
            values = re.findall(pattern, answer)
            data=[]
            for value in values:
                if value[0] != "": data.append(value[0])
                else: data.append(value[1])

            simdata = {"type": data[0], "charge": data[1], "mass": data[2], "v0": data[3], "B": data[4]}
            if simdata["type"] == "None" and simdata["charge"] == "None" and simdata["mass"] == "None":
                simdata["type"] = "electron"
            if simdata["v0"] == "None": simdata["v0"] = 1e6
            if simdata["B"] == "None": simdata["B"] = 3
            return simdata 


        except:
                print("error with groq call")
                return False

    answers = []
    v = False
    falseCount = 0
    while v == False:
        answer = getAnswer()
        #print("call")
        if answer != False:
            answers.append(answer)
            if len(answers) > 0:
                for i in range(0, len(answers)-1):
                    if answer == answers[i]: 
                        v = True
        else: falseCount += 1
        if falseCount == 3: return False

    return answer