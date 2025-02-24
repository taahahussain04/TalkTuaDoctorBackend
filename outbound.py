import asyncio

from livekit import api
from livekit.protocol.sip import CreateSIPOutboundTrunkRequest, SIPOutboundTrunkInfo
from livekit.protocol.sip import CreateSIPParticipantRequest, SIPParticipantInfo


async def main():
  livekit_api = api.LiveKitAPI(
    url="wss://talktuahdoctor-5gb81v9o.livekit.cloud",  
    api_key="API6YWrN7juMRYy",                 
    api_secret="Y0ssBcfn7lXVJAuUEalD0m4Ff1pmVlK7iBfpDyj1Q6ZB"            
  )


  trunk = SIPOutboundTrunkInfo(
    name = "TalkTuahTrunk",
    address = "ttd2.pstn.twilio.com",
    numbers = ['+19804738922'],
    auth_username = "yshaikh",
    auth_password = "nbaVyqv8bMXLrqy"
  )

#   request = CreateSIPParticipantRequest(
#     sip_trunk_id = "ST_izh8AR6UNGqp",
#     sip_call_to = "+16175043703",
#     room_name = "ttd",
#     participant_identity = "Agent",
#     participant_name = "Yusuf",
#     krisp_enabled = True,
#   )
  
  request = CreateSIPOutboundTrunkRequest(trunk = trunk)

  trunk = await livekit_api.sip.create_sip_outbound_trunk(request)

  print(f"Successfully created {trunk}")

  await livekit_api.aclose()

asyncio.run(main())


