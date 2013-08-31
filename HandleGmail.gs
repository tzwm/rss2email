function main() {
  var threads = GmailApp.getInboxThreads();
  for (var i = 0; i < threads.length; i++) {
    var messages = threads[i].getMessages();
    
    var tag = messages[0].getTo();
    if (tag.search(/\+/) != -1) {
      tag = tag.substring(tag.search(/\+/)+1, tag.search(/\@/));
      tag = tag.replace(/\+/, "/");
      
      var tagTmp = tag + "/";
      var tagTmp1 = "";
      while(tagTmp.search(/\//) != -1) {
        if (tagTmp1 != "") {
          tagTmp1 = tagTmp1 + "/";
        }
        tagTmp1 = tagTmp1 + tagTmp.substring(0, tagTmp.search(/\//));
        if (!GmailApp.getUserLabelByName(tagTmp1)) {
          GmailApp.createLabel(tagTmp1);
        }
        tagTmp = tagTmp.substring(tagTmp.search(/\//)+1);
      }
    }
    else {
      tag = "";
    }
    
    var subject = messages[0].getSubject();
    subject = subject.substring(subject.search(/\[/)+1, subject.search(/\]/));
    tag = tag + "/" + subject;
    if (!GmailApp.getUserLabelByName(tag)) {
      Utilities.sleep(500);
      GmailApp.createLabel(tag);
    }
    
    var label = GmailApp.getUserLabelByName(tag);
    threads[i].addLabel(label);

    Utilities.sleep(500);
//    break;
  }
};


