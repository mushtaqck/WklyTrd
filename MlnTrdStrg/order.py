from ghost import Ghost

class IDirectBroker(object):
    
    IDIRECTURL = 'https://secure.icicidirect.com/Trading/LBS/Logon.asp'

    def __init__(self,username, password, **kwargs):
        self.username = username
        self.password = password
        self.ghost = Ghost()



        try:
            self.page, self.resources = self.ghost.open(self.IDIRECTURL)
            
            self.ghost.wait_for_page_loaded()
            self.ghost.capture_to("./l1.png")
            
            result, resources = self.ghost.fill("form", { "FML_USR_ID": "MUSE9L71", "FML_USR_USR_PSSWRD": "Infotech@8","FML_USR_DT_BRTH":"22101982" })
            self.ghost.capture_to("./l2.png")
            self.page, self.resources = self.ghost.fire("form", "submit", expect_loading=True)
            #self.ghost.wait_for_page_loaded()
            self.ghost.capture_to("./l3.png")

        except Exception,e:
            raise e


if __name__ == '__main__':
    b = IDirectBroker("","")







